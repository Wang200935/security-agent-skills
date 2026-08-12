# Modprobe Path AF_ALG Bypass (2025)

Upstream kernel v6.14-rc1 removed the `request_module()` call from `search_binary_handler()`. Executing dummy files with unknown magic bytes NO LONGER triggers `modprobe_path` on upstream kernels.

**New trigger method**: `AF_ALG` socket `bind()` with dummy type string → `alg_bind()` → `request_module("algif-%s")` → `call_modprobe()` → executes `modprobe_path[]` as root.

**Fileless chaining**: `memfd_create()` + write modprobe script + dup → overwrite `modprobe_path[]` with `/proc/<pid>/fd/<memfd>` → bind AF_ALG socket → root shell.

Reference:
