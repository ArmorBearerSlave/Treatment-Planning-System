function pytps_matrad_plan(job, library)
% pytps matRad bridge: photon dose calculation and fluence optimisation.
%
% Nonclinical research adapter. It uses a separately installed matRad; no
% matRad source is copied here and the matRad checkout is not written to.
% matRad userdata for this run stays inside the job folder.
%
% Contract
%   job      folder holding job.json, source.json, request.json, ct.f32,
%            labels.i16, all frozen and hashed by pytps before submission.
%   library  root of the matRad checkout.
%
% Two modes, selected by request.mode.
%   'optimize' (default) runs fluence optimisation and emits total-course
%              physical Gy. A nonconverged optimisation writes plan.mat and
%              the log but deliberately emits no dose.
%   'forward'  skips optimisation and emits the dose of a uniform open field
%              (every bixel weight 1). Nothing is optimised, so this isolates
%              the dose engine from the optimiser when comparing against
%              another planning system. The result is on an arbitrary scale
%              and the caller normalises it.
%
% Output is dose.f32 (X-fastest XYZ float32 little-endian) and result.json.

narginchk(2,2);
job = char(job); library = char(library);

j = jsondecode(fileread(fullfile(job,'job.json')));
assert(j.schemaVersion == 1, 'pytps:schema', 'Unsupported job schema version');
assert(strcmp(j.kind,'matrad'), 'pytps:kind', 'Job is not a matRad job');
assert(~j.clinicalUsePermitted, 'pytps:clinical', 'Job claims clinical use');

% Nothing is computed until every frozen input still hashes to what pytps froze.
for i = 1:numel(j.inputs)
    entry = j.inputs(i);
    assert(strcmp(pytps_filehash(fullfile(job,entry.file)), entry.sha256), ...
        'pytps:frozen', 'Frozen input changed before execution: %s', entry.file);
end

s = jsondecode(fileread(fullfile(job,'source.json')));
r = jsondecode(fileread(fullfile(job,'request.json')));
assert(s.syntheticOnly, 'pytps:synthetic', 'Only synthetic cases are accepted');

g = s.grid;
n = double(g.dimensions(:)');
assert(isequal(g.direction(:)', [1 0 0 0 1 0 0 0 1]), 'pytps:oblique', 'Oblique grids are unsupported');
res = double(g.spacing(:)');
org = double(g.origin(:)');

ctFlat     = pytps_readvolume(fullfile(job,'ct.f32'),    'float32', prod(n));
labelsFlat = pytps_readvolume(fullfile(job,'labels.i16'),'int16',   prod(n));

% pytps stores X-fastest XYZ; matRad cubes are [Y X Z]. Explicit permutation,
% no rotation, no resampling, original LPS axis coordinates retained.
ct = struct();
ct.cubeDim    = n([2 1 3]);
ct.cubeHU     = {permute(reshape(double(ctFlat), n), [2 1 3])};
labels        = permute(reshape(double(labelsFlat), n), [2 1 3]);
ct.resolution = struct('x',res(1),'y',res(2),'z',res(3));
ct.x = org(1) + (0:n(1)-1)*res(1);
ct.y = org(2) + (0:n(2)-1)*res(2);
ct.z = org(3) + (0:n(3)-1)*res(3);
ct.numOfCtScen = 1;

% A saved MATLAB path can already contain another matRad or CERR checkout,
% which would shadow the one this job recorded. Start from the default path so
% the run is reproducible, then add only what this job asked for. The adapter
% helpers live beside this file in the job folder.
restoredefaultpath;
addpath(job);
addpath(library);
cfg = matRad_rc;
cfg.userfolders = {fullfile(job,'userdata')};
if isfield(r,'maxIterations') && ~isempty(r.maxIterations)
    cfg.defaults.propOpt.maxIter = double(r.maxIterations);
end
set(0,'DefaultFigureVisible','off');

% Verify empirically that matRad's world frame is the LPS frame pytps sent,
% rather than trusting a reading of matRad's coordinate helpers.
probeSub = [2 3 2];
probeSub = min(probeSub, ct.cubeDim);
probeIdx = sub2ind(ct.cubeDim, probeSub(1), probeSub(2), probeSub(3));
probeWorld = matRad_cubeIndex2worldCoords(probeIdx, ct);
expectWorld = [ct.x(probeSub(2)) ct.y(probeSub(1)) ct.z(probeSub(3))];
assert(max(abs(probeWorld(:)' - expectWorld)) < 1e-6, 'pytps:frame', ...
    'matRad world coordinates do not match the supplied LPS axes');

structures = s.structures;
target = '';
cst = cell(numel(structures), 6);
for k = 1:numel(structures)
    st = structures(k);
    voxels = find(labels == st.label);
    cst{k,1} = k-1;
    cst{k,2} = st.name;
    cst{k,3} = 'OAR';
    cst{k,4} = {voxels};
    cst{k,5} = struct('TissueClass',1,'alphaX',0.1,'betaX',0.05, ...
                      'Priority',k+1,'Visible',true,'visibleColor',double(st.color(:)'));
    cst{k,6} = {};
end

% Objectives come from pytps by structure name. matRad's squared objectives use
% the same 1/numel(dose) * sum(residual^2) normalisation as pytps, so the same
% weights describe the same function; only the dose engine differs.
for i = 1:numel(r.objectives)
    o = r.objectives(i);
    k = find(strcmp({structures.name}, o.structure), 1);
    assert(~isempty(k), 'pytps:objective', 'Objective names an unknown structure: %s', o.structure);
    assert(~isempty(cst{k,4}{1}), 'pytps:empty', 'Objective structure is empty: %s', o.structure);
    switch o.type
        case 'target_dose'
            obj = DoseObjectives.matRad_SquaredDeviation(o.weight, o.doseGy);
            cst{k,3} = 'TARGET';
            cst{k,5}.Priority = 1;
            target = o.structure;
        case 'max_dose'
            obj = DoseObjectives.matRad_SquaredOverdosing(o.weight, o.doseGy);
        case 'min_dose'
            obj = DoseObjectives.matRad_SquaredUnderdosing(o.weight, o.doseGy);
        otherwise
            error('pytps:objective', 'Objective type %s has no matRad equivalent', o.type);
    end
    cst{k,6}{end+1} = struct(obj);
end
assert(~isempty(target), 'pytps:target', 'No target objective was supplied');

% Unlabelled voxels stay a scoring region with no objective. No contour is invented.
if any(labels(:) == 0)
    k = size(cst,1) + 1;
    cst(k,:) = {k-1, 'Unlabelled scoring voxels', 'OAR', {find(labels == 0)}, ...
        struct('TissueClass',1,'alphaX',0.1,'betaX',0.05,'Priority',k+1,'Visible',false), {}};
end

pln = struct();
pln.radiationMode = 'photons';
pln.machine       = 'Generic';
pln.bioModel      = 'none';
pln.multScen      = 'nomScen';
pln.numOfFractions = double(r.fractions);
pln.propStf.gantryAngles = double(r.gantryAnglesDeg(:)');
pln.propStf.couchAngles  = zeros(size(pln.propStf.gantryAngles));
pln.propStf.bixelWidth   = double(r.bixelWidthMM);
pln.propStf.numOfBeams   = numel(pln.propStf.gantryAngles);
matRadIso = matRad_getIsoCenter(cst, ct, 0);
pln.propStf.isoCenter = repmat(matRadIso, pln.propStf.numOfBeams, 1);
pln.propOpt.runDAO = false;
pln.propOpt.runSequencing = false;
pln.propOpt.quantityOpt = 'physicalDose';
pln.propDoseCalc.doseGrid = struct('resolution',ct.resolution,'x',ct.x,'y',ct.y,'z',ct.z);

% pytps places the isocentre at the target centroid; matRad computes its own.
% Record the disagreement rather than silently planning a shifted geometry.
isoDeltaMM = matRadIso(:)' - double(r.isocenterMM(:)');
assert(max(abs(isoDeltaMM)) <= double(r.isocenterToleranceMM), 'pytps:isocenter', ...
    'matRad isocentre differs from the requested one by %s mm', mat2str(isoDeltaMM,4));

ct  = matRad_calcWaterEqD(ct, 'photons');
stf = matRad_generateStf(ct, cst, pln);
dij = matRad_calcDoseInfluence(ct, cst, stf, pln);
assert(isequal(dij.doseGrid.x,ct.x) && isequal(dij.doseGrid.y,ct.y) && isequal(dij.doseGrid.z,ct.z), ...
    'pytps:dosegrid', 'Dose grid axes differ from the CT');
assert(isequal(dij.doseGrid.dimensions, ct.cubeDim), 'pytps:dosegrid', 'Dose grid dimensions differ from the CT');

mode = 'optimize';
if isfield(r,'mode') && ~isempty(r.mode)
    mode = char(r.mode);
end
assert(ismember(mode,{'optimize','forward'}), 'pytps:mode', 'Unknown mode %s', mode);

if strcmp(mode,'forward')
    % Uniform open field: every bixel carries weight 1 and nothing is
    % optimised, so a comparison against another code sees the dose engine
    % alone. The scale is arbitrary and the caller normalises.
    weights = ones(dij.totalNumOfBixels, 1);
    doseVector = dij.physicalDose{1} * weights;
    doseCube = permute(reshape(full(doseVector), dij.doseGrid.dimensions), [2 1 3]);
    optimizer = [];
    converged = true;
    doseBasis = 'relative-uniform-fluence';
    resultGUI = struct('w', weights, 'info', struct('mode','forward'));
else
    [resultGUI, optimizer] = matRad_fluenceOptimization(dij, cst, pln);
    assert(all(isfinite(resultGUI.w)) && all(resultGUI.w >= 0), 'pytps:weights', 'Invalid optimised weights');
    weights = resultGUI.w;
    % matRad divides course objectives by the fraction count and returns
    % physical per-fraction dose. Multiply back exactly once. No renormalisation.
    doseCube = permute(resultGUI.physicalDose, [2 1 3]) * pln.numOfFractions;
    converged = (isa(optimizer,'matRad_OptimizerFmincon') && resultGUI.info.exitflag > 0) || ...
                (isa(optimizer,'matRad_OptimizerIPOPT')   && ismember(resultGUI.info.status,[0 1]));
    doseBasis = 'total-course-physical-Gy';
end
assert(isequal(size(doseCube), n), 'pytps:shape', 'Dose dimensions changed');
assert(all(isfinite(doseCube(:))) && all(doseCube(:) >= 0) && any(doseCube(:) > 0), ...
    'pytps:dose', 'Invalid optimised dose');

evidence = struct();
evidence.matRadVersion = char(matRad_version());
evidence.MATLABVersion = version;
evidence.computer      = computer;
evidence.machine       = 'Generic photons (uncommissioned)';
evidence.machineSHA256 = pytps_filehash(which('photons_Generic.mat'));
evidence.hlutSHA256    = pytps_filehash(fullfile(library,'matRad','hluts','matRad_default.hlut'));
evidence.adapterSHA256 = pytps_filehash([mfilename('fullpath') '.m']);
evidence.calcDoseSHA256 = pytps_filehash(which('matRad_calcDoseInfluence'));
evidence.optimizationSHA256 = pytps_filehash(which('matRad_fluenceOptimization'));
evidence.mode          = mode;
if isempty(optimizer)
    evidence.optimizer = 'none (forward dose, uniform fluence)';
else
    evidence.optimizer = class(optimizer);
end
evidence.maxIterations = cfg.defaults.propOpt.maxIter;
evidence.matRadRoot    = fileparts(fileparts(which('matRad_calcDoseInfluence')));
evidence.pathPolicy    = 'restoredefaultpath, then the job folder and the recorded library only';
evidence.isocenterMM   = matRadIso(:)';
evidence.isocenterDeltaMM = isoDeltaMM;
evidence.bixelCount    = numel(weights);
if strcmp(mode,'forward')
    evidence.normalization = 'Uniform unit fluence; arbitrary scale, normalised by the caller';
else
    evidence.normalization = 'Per-fraction physical dose multiplied by the requested fractions; no renormalization';
end
evidence.geometry      = 'pytps X-fastest XYZ <-> matRad YXZ; LPS axes retained; no resampling';
evidence.scope         = 'Research fluence optimisation. No sequencing, deliverability, or biological model.';
evidence.optimizerConverged = converged;
evidence.optimizerInfo = evalc('disp(resultGUI.info)');

save(fullfile(job,'plan.mat'), 'ct','cst','pln','stf','resultGUI','evidence','-v7.3');
assert(converged, 'pytps:converged', ...
    ['Optimiser did not converge after %d iterations; plan.mat and the log are retained ' ...
     'and no dose is emitted. Raise the iteration limit if the trajectory was still improving.'], ...
    cfg.defaults.propOpt.maxIter);

dosePath = fullfile(job,'dose.f32');
fid = fopen(dosePath,'w','ieee-le');
assert(fid >= 0, 'pytps:write', 'Cannot write dose.f32');
closer = onCleanup(@() fclose(fid));
% doseCube is [X Y Z]; MATLAB's column-major linear order is X-fastest,
% which is exactly the layout pytps reads back.
fwrite(fid, single(doseCube(:)), 'float32');
clear closer;

out = struct();
out.schemaVersion = 1;
out.kind = 'matrad';
out.jobID = j.jobID;
out.sourceDigest = pytps_filehash(fullfile(job,'source.json'));
out.requestDigest = pytps_filehash(fullfile(job,'request.json'));
out.clinicalReleaseAllowed = false;
out.doseBasis = doseBasis;
out.doseFile = 'dose.f32';
out.doseDigest = pytps_filehash(dosePath);
out.doseDtype = 'float32';
out.doseLayout = 'X-fastest XYZ';
out.weights = weights(:)';
out.evidence = evidence;
pytps_writejson(fullfile(job,'result.json'), out);
fprintf('pytps matRad result ready: %s\n', fullfile(job,'result.json'));
end
