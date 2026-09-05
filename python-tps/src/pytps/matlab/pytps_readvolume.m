function values = pytps_readvolume(path, precision, expectedCount)
% Read a raw little-endian volume written by pytps.
%
% Layout is X-fastest XYZ, so the returned column vector can be reshaped
% directly with the [nx ny nz] dimensions. The element count is checked, so a
% truncated or mis-typed file fails here rather than producing a plausible
% but wrong cube.
path = char(path);
fid = fopen(path, 'rb', 'ieee-le');
assert(fid >= 0, 'pytps:read', 'Cannot open volume: %s', path);
closer = onCleanup(@() fclose(fid));
values = fread(fid, Inf, ['*' precision]);
clear closer;
assert(numel(values) == expectedCount, 'pytps:count', ...
    'Volume %s holds %d values, expected %d', path, numel(values), expectedCount);
assert(all(isfinite(double(values))), 'pytps:finite', 'Volume %s contains non-finite values', path);
end
