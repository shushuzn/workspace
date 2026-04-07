@echo off
curl -x http://127.0.0.1:7897 -L --retry 3 --max-time 600 --progress-bar -o "%USERPROFILE%\.cache\huggingface\hub\models--runwayml--stable-diffusion-v1-5\snapshots\451f4fe16113bff5a5d2269ed5ad43b0592e9a14\unet\diffusion_pytorch_model.safetensors" "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/unet/diffusion_pytorch_model.safetensors"
