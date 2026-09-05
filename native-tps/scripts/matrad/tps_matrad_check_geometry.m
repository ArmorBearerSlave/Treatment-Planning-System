function tps_matrad_check_geometry(job)
% Independent index-by-index check using a saved plan and adapter result.
a = load(fullfile(job,'plan.mat'),'ct','resultGUI','pln');
s = jsondecode(fileread(fullfile(job,'source.json')));
r = jsondecode(fileread(fullfile(job,'result.json')));
n = s.ct.grid.dimensions;
assert(numel(unique(n))==3 && numel(unique(s.ct.grid.spacing))==3,'Use an asymmetric fixture');
for z=1:n(3)
    for y=1:n(2)
        for x=1:n(1)
            i = (z-1)*n(1)*n(2)+(y-1)*n(1)+x;
            assert(a.ct.cubeHU{1}(y,x,z)==s.ct.values(i),'CT index orientation mismatch');
            expected = a.resultGUI.physicalDose(y,x,z)*a.pln.numOfFractions;
            assert(abs(r.volume.values(i)-expected)<1e-10,'Dose order or fraction scaling mismatch');
        end
    end
end
assert(a.pln.numOfFractions==5,'Five-fraction test expected');
fprintf('PASS: all asymmetric CT indices and five-fraction dose values match the saved MATLAB plan.\n');
end
