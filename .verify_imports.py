import importlib
mods = ['torch','torchvision','transformers','sklearn','xgboost','sentence_transformers','pandas','numpy']
for m in mods:
    try:
        mod = importlib.import_module(m)
        ver = getattr(mod, '__version__', 'n/a')
        print(f"OK {m} {ver}")
    except Exception as e:
        print(f"FAIL {m}: {e}")
import torch
print('torch cuda available:', torch.cuda.is_available())
