# Offline backup

`requirements.txt` records the installed Python environment, including
Transformers 4.57.3. Saved workflows are in `user/default/workflows/`.
Custom nodes are committed as ordinary files, including local changes.

This is a source backup, not a complete offline installation. Models, the Python
environment, login credentials, private configuration, caches, and compiled custom
node libraries are excluded. Back these up separately for an offline restore;
QuantFunc requires its matching compiled engine libraries.

Nested custom-node Git metadata is excluded. Source revisions at backup:

- ComfyUI-Image-Filters: f73e586470e0d65a7372b328d4bccbabfc94c180
- ComfyUI-LTXVideo: 36fdaf500b3cd6f7fa8b2dfec36e984746e630a2
- ComfyUI-Login: 69109257f4629a11ebe26cd65667536c4f8dddcb
- ComfyUI-Manager: ae66bd0e31da253acd2468e94ea018ea6c201f77
- ComfyUI-QuantFunc: ccb5e73a24139b0d40fb741919a519fbd332906a
- H3-Character-Sheet-Designer: 6ff492c1534a6edb37d694197e6c8d2aa2764edf
