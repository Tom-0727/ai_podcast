# huggingface-cli download ByteDance/MegaTTS3 --local-dir ./checkpoints 

export PYTHONPATH="/home/tom/codes/MegaTTS3:$PYTHONPATH"
CUDA_VISIBLE_DEVICES="" python tts/infer_cli.py --input_wav 'assets/Chinese_prompt.wav'  --input_text "我是超大汤姆猫，怎么说？呜呜呜我真的好想要吃阿达西烧烤加四果汤外加超大块南蛮鸭的蛋糕！" --output_dir ./gen