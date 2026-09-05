function hash = pytps_filehash(path)
% SHA-256 of a file, as lowercase hex. Used to bind results to frozen inputs.
% This is a local integrity digest, not an authenticated signature.
path = char(path);
fid = fopen(path,'rb');
assert(fid >= 0, 'pytps:hash', 'Cannot open file for hashing: %s', path);
closer = onCleanup(@() fclose(fid));
md = java.security.MessageDigest.getInstance('SHA-256');
while ~feof(fid)
    bytes = fread(fid, 1048576, '*uint8');
    if ~isempty(bytes)
        md.update(bytes);
    end
end
hash = lower(reshape(dec2hex(typecast(md.digest(),'uint8'),2)', 1, []));
end
