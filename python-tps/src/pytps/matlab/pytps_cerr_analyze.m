function pytps_cerr_analyze(job, library)
% pytps CERR bridge: independent dose-volume analysis of a pytps dose.
%
% Nonclinical research adapter. It uses a separately installed CERR; no CERR
% source is copied here and the CERR checkout is not written to. It imports no
% patient DICOM: the planC it builds is assembled entirely from the synthetic
% arrays pytps froze into this job folder.
%
% Two things are established, in this order.
%   1. A geometry round trip. LPS millimetres become CERR's [L,-P,-S]
%      centimetre frame with reversed slices, and every scan axis, dose axis,
%      CT voxel and dose voxel is read back and compared against what was sent.
%      Nothing is analysed until those comparisons are exact.
%   2. An independent dose-volume measurement, using CERR's own getDVH
%      sampling and doseHist binning rather than pytps's histogram code.
%
% Contract
%   job      folder with job.json, source.json, request.json, ct.f32,
%            labels.i16 and dose.f32, all frozen and hashed by pytps.
%   library  root of the CERR checkout.

narginchk(2,2);
job = char(job); library = char(library);

j = jsondecode(fileread(fullfile(job,'job.json')));
assert(j.schemaVersion == 1, 'pytps:schema', 'Unsupported job schema version');
assert(strcmp(j.kind,'cerr'), 'pytps:kind', 'Job is not a CERR job');
assert(~j.clinicalUsePermitted, 'pytps:clinical', 'Job claims clinical use');
for i = 1:numel(j.inputs)
    entry = j.inputs(i);
    assert(strcmp(pytps_filehash(fullfile(job,entry.file)), entry.sha256), ...
        'pytps:frozen', 'Frozen input changed before execution: %s', entry.file);
end

s = jsondecode(fileread(fullfile(job,'source.json')));
r = jsondecode(fileread(fullfile(job,'request.json')));
assert(s.syntheticOnly, 'pytps:synthetic', 'Only synthetic cases are accepted');

g = s.grid;
n  = double(g.dimensions(:)');
sp = double(g.spacing(:)');
org = double(g.origin(:)');
assert(isequal(g.direction(:)', [1 0 0 0 1 0 0 0 1]), 'pytps:oblique', 'Oblique grids are unsupported');
assert(r.binWidthGy > 0, 'pytps:bins', 'Histogram bin width must be positive');

ctFlat     = pytps_readvolume(fullfile(job,'ct.f32'),    'float32', prod(n));
labelsFlat = pytps_readvolume(fullfile(job,'labels.i16'),'int16',   prod(n));
doseFlat   = pytps_readvolume(fullfile(job,'dose.f32'),  'float32', prod(n));
assert(all(double(doseFlat) >= 0), 'pytps:dose', 'Dose must be non-negative');
assert(max(double(doseFlat))/r.binWidthGy <= 20000, 'pytps:bins', 'Bin width gives too many bins');

% As in the matRad adapter: start from the default path so a matRad checkout
% already on the saved MATLAB path cannot shadow CERR, or the reverse.
restoredefaultpath;
addpath(job);
addpath(library);
addToPath(library);
planC = initializeCERR;
ix = planC{end};
planC{ix.CERROptions} = struct('ROISampleRate',1,'DVHBlockSize',50);

% CERR research coordinates are [L,-P,-S] in centimetres, with slices ordered
% by ascending CERR z, which is descending LPS z.
x = (org(1) + (0:n(1)-1)*sp(1)) / 10;
y = -(org(2) + (0:n(2)-1)*sp(2)) / 10;
z = -fliplr(org(3) + (0:n(3)-1)*sp(3)) / 10;

ctCube     = flip(permute(reshape(double(ctFlat),     n), [2 1 3]), 3);
labelsCube = flip(permute(reshape(double(labelsFlat), n), [2 1 3]), 3);
doseCube   = flip(permute(reshape(double(doseFlat),   n), [2 1 3]), 3);

scan = initializeCERR('scan');
scan(1).scanArray = ctCube;
scan(1).scanType  = 'CT';
scan(1).scanUID   = ['pytps-' s.caseID];
scan(1).transM    = [];
info = initializeScanInfo;
info(1).grid1Units = sp(2)/10;
info(1).grid2Units = sp(1)/10;
info(1).sizeOfDimension1 = n(2);
info(1).sizeOfDimension2 = n(1);
info(1).xOffset = mean(x);
info(1).yOffset = mean(y);
info(1).CTOffset = 0;
info(1).imageType = 'CT';
info(1).sliceThickness = sp(3)/10;
for k = 1:n(3)
    info(1).zValue = z(k);
    scan(1).scanInfo(k) = info(1);
end
planC{ix.scan} = scan;

d = initializeCERR('dose');
d(1).doseArray = doseCube;
d(1).doseUnits = 'GY';
d(1).doseScale = 1;
d(1).doseOffset = 0;
d(1).assocScanUID = scan(1).scanUID;
d(1).doseUID = ['pytps-dose-' j.jobID];
d(1).horizontalGridInterval = sp(1)/10;
d(1).verticalGridInterval = -sp(2)/10;
d(1).coord1OFFirstPoint = x(1);
d(1).coord2OFFirstPoint = y(1);
d(1).sizeOfDimension1 = n(1);
d(1).sizeOfDimension2 = n(2);
d(1).sizeOfDimension3 = n(3);
d(1).zValues = z;
d(1).transM = [];
planC{ix.dose} = d;

% Round trip 1: axes as CERR reports them.
[sx,sy,sz] = getScanXYZVals(scan(1));
[dx,dy,dz] = getDoseXYZVals(d(1));
assert(max(abs(sx-x)) < 1e-9 && max(abs(sy-y)) < 1e-9 && max(abs(sz-z)) < 1e-9, ...
    'pytps:coords', 'Scan coordinate conversion failed');
assert(max(abs(dx-x)) < 1e-9 && max(abs(dy-y)) < 1e-9 && max(abs(dz-z)) < 1e-9, ...
    'pytps:coords', 'Dose coordinate conversion failed');

% Round trip 2: voxels, byte for byte, back in pytps X-fastest order.
backCT = permute(flip(getScanArray(scan(1)), 3), [2 1 3]);
assert(isequal(double(backCT(:)), double(ctFlat(:))), 'pytps:roundtrip', 'CT voxel round trip failed');
backDose = permute(flip(getDoseArray(1, planC), 3), [2 1 3]);
assert(isequal(double(backDose(:)), double(doseFlat(:))), 'pytps:roundtrip', 'Dose voxel round trip failed');

% Structures are the supplied label masks, rasterised exactly as row runs.
% No polygon is reconstructed and no contour is invented.
structures = s.structures;
kept = [];
for k = 1:numel(structures)
    st = initializeCERR('structures');
    st(1).structureName = structures(k).name;
    st(1).assocScanUID  = scan(1).scanUID;
    st(1).strUID        = sprintf('pytps-label-%d', structures(k).label);
    st(1).structureColor = double(structures(k).color(:)');
    st(1).rasterized = 1;
    runs = cell(n(2)*n(3),1);
    row = 0;
    for iz = 1:n(3)
        for iy = 1:n(2)
            mask = labelsCube(iy,:,iz) == structures(k).label;
            starts = find(diff([false mask false]) == 1);
            stops  = find(diff([false mask false]) == -1) - 1;
            segment = zeros(numel(starts), 10);
            for q = 1:numel(starts)
                segment(q,:) = [z(iz), y(iy), x(starts(q)), x(stops(q)), sp(1)/10, ...
                                iz, iy, starts(q), stops(q), sp(3)/10];
            end
            row = row + 1;
            runs{row} = segment;
        end
    end
    st(1).rasterSegments = vertcat(runs{:});
    if isempty(st(1).rasterSegments)
        continue;
    end
    planC{ix.structures}(numel(kept)+1) = st;
    kept(end+1) = k; %#ok<AGROW>
end
assert(~isempty(kept), 'pytps:structures', 'No non-empty structures to analyse');

records = {};
for q = 1:numel(kept)
    k = kept(q);
    expected = doseCube(labelsCube == structures(k).label);
    [samples, volumes, isError] = getDVH(q, 1, planC);
    assert(~isError, 'pytps:dvh', 'CERR getDVH reported an error for %s', structures(k).name);
    assert(numel(samples) == numel(expected), 'pytps:dvh', ...
        'CERR sampled %d voxels for %s, pytps has %d', numel(samples), structures(k).name, numel(expected));
    assert(all(isfinite(samples)) && all(samples >= 0), 'pytps:dvh', 'Invalid CERR dose samples');
    assert(all(isfinite(volumes)) && all(volumes > 0), 'pytps:dvh', 'Invalid CERR voxel volumes');

    [binCenters, differential] = doseHist(samples, volumes, r.binWidthGy);
    totalVolume = sum(volumes);
    sorted = sort(samples(:), 'descend');
    rec = struct();
    rec.label = structures(k).label;
    rec.name = structures(k).name;
    rec.sampleCount = numel(samples);
    rec.volumeCC = totalVolume;
    rec.meanGy = sum(samples(:) .* volumes(:)) / totalVolume;
    rec.minGy = min(samples);
    rec.maxGy = max(samples);
    % Nearest-rank Dx on descending samples with equal voxel volumes, which is
    % the definition pytps reproduces for the comparison.
    for frac = [0.02 0.50 0.95 0.98]
        rank = max(1, ceil(frac * numel(sorted)));
        rec.(sprintf('d%02dGy', round(frac*100))) = sorted(rank);
    end
    rec.maxSampleDifferenceGy = max(abs(sort(samples(:)) - sort(double(expected(:)))));
    rec.binCentersGy = binCenters(:)';
    rec.differentialVolumeCC = differential(:)';
    records{end+1} = rec; %#ok<AGROW>
end

evidence = struct();
evidence.MATLABVersion = version;
evidence.computer = computer;
evidence.libraryRoot = library;
evidence.pathPolicy = 'restoredefaultpath, then the job folder and the recorded library only';
evidence.getDVHSHA256 = pytps_filehash(which('getDVH'));
evidence.doseHistSHA256 = pytps_filehash(which('doseHist'));
evidence.adapterSHA256 = pytps_filehash([mfilename('fullpath') '.m']);
evidence.geometry = 'LPS mm -> CERR [L,-P,-S] cm, YXZ with reversed slices; axis and voxel round trips verified exactly';
evidence.structures = 'Exact label-mask row runs; no polygon reconstruction';
evidence.sampling = 'CERR getDVH with ROISampleRate 1 on the original scan and dose grid';
evidence.dxDefinition = 'Nearest rank ceil(fraction * N) on descending sorted samples, equal voxel volumes';
evidence.binWidthGy = r.binWidthGy;
evidence.scope = 'Analysis only. No dose recalculation, no calibration, no clinical release.';

save(fullfile(job,'planC.mat'), 'planC', 'evidence', '-v7.3');
out = struct();
out.schemaVersion = 1;
out.kind = 'cerr';
out.jobID = j.jobID;
out.sourceDigest = pytps_filehash(fullfile(job,'source.json'));
out.requestDigest = pytps_filehash(fullfile(job,'request.json'));
out.doseDigest = pytps_filehash(fullfile(job,'dose.f32'));
out.clinicalReleaseAllowed = false;
out.records = records;
out.evidence = evidence;
pytps_writejson(fullfile(job,'report.json'), out);
fprintf('pytps CERR analysis ready for %d structures: %s\n', numel(records), fullfile(job,'report.json'));
end
