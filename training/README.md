# How to train the Skin-Check AI model (step by step)

You'll train the model yourselves on Google Colab — it's free, uses Google's GPUs,
and takes about 30 minutes total. You only need to do this once.

## What you need
- A Google account (for [colab.google](https://colab.google))
- A free [Kaggle](https://www.kaggle.com) account (the HAM10000 dataset is hosted there)

## Steps

1. Go to [colab.google](https://colab.google) → **Open Colab** → **Upload** →
   choose `train_skin_model.ipynb` from this folder.
2. In Colab's menu: **Runtime → Change runtime type → T4 GPU** → Save.
3. **Runtime → Run all.** The Kaggle download cell will ask you to log in — follow the
   link it prints and paste the token. Then wait (~20–30 min).
   - If a cell errors right after the installs, do **Runtime → Restart session and run all** once.
4. When it finishes, your browser downloads **`skin_model.zip`**. Write down the
   accuracy, sensitivity and specificity it printed — you'll want them for your report.
5. Unzip it and copy **all the files** (`model.json`, `group1-shard*.bin`, `metrics.json`)
   into the `static/model/` folder of this repo.
6. Commit and push:
   ```bash
   git add static/model
   git commit -m "Add trained skin-check model"
   git push
   ```
7. Open the website → **AI Skin Check** — the page detects the model automatically and
   shows your real test accuracy at the top.

## About the dataset

HAM10000 ("Human Against Machine with 10000 training images") — 10,015 dermatoscopic
images of skin lesions, published for research by Tschandl, Rosendahl & Kittler (2018).
The notebook groups its 7 diagnosis types into **benign** (moles, benign keratoses,
dermatofibroma, vascular lesions) vs **suspicious** (melanoma, basal cell carcinoma,
actinic keratoses).

## Honest limits (say these in your presentation — judges love it)

- The model compares a photo to its training images; it cannot diagnose anyone.
- HAM10000 photos were taken with a dermatoscope (a special magnifying tool), so
  ordinary phone photos look different — expect real-world accuracy to be lower
  than the test-set number.
- The dataset contains mostly lighter skin tones, so the model may be less reliable
  on darker skin — a known, published problem in dermatology AI worth mentioning.
