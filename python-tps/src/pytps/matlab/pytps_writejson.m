function pytps_writejson(path, payload)
% Write a result document atomically, so a partial file is never importable.
path = char(path);
temporary = [path '.tmp'];
fid = fopen(temporary, 'w');
assert(fid >= 0, 'pytps:write', 'Cannot write %s', temporary);
closer = onCleanup(@() fclose(fid));
fprintf(fid, '%s', jsonencode(payload));
clear closer;
[ok, message] = movefile(temporary, path, 'f');
assert(ok, 'pytps:write', 'Cannot finalise %s: %s', path, message);
end
