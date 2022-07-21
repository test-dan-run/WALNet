# WALNet
This is a re-implementation of the [official WALNet repository](https://github.com/ankitshah009/WALNet-Weak_Label_Analysis).

## New Things

- [x] [Hydra](https://hydra.cc/docs/intro/) to manage our pipeline configurations
- [x] [PyTorch Lightning](https://www.pytorchlightning.ai/) to abstract away tedious code, and enforce a standard experiment code structure
- [x] [yt-dlp](https://github.com/yt-dlp/yt-dlp) to manage the downloading of data from Youtube. It allows us to download only the required segments of a video, rather than the entire video before processing, saving downloading duration by 50x
- [x] Reorganized the code for better readability
- [x] Allows loading data on-the-fly, instead of preprocessing all dataset features before training. This enables transformations on-the-fly later on for training more robust models

## TODOs

- [ ] Add logging features
- [ ] Add label corruption features
- [x] Documentation

## How to Run Experiments

### 1. Use docker!

Build the docker image with the required dependicies in the `build` folder via this command.
```bash
cd build
docker build -t dleongsh/torchaudio:1.8.1-cuda11.1-cudnn8-runtime .
```

Then, change the paths to your directories in the `docker-compose.yaml` file as you see fit.

### 2. Set your configs
First set your dataset manifest paths in the `configs/dataset/audioset.yaml` file. They should correspond to the mapped dataset volume as stated in your updated `docker-compose.yaml` file. As an example:

My local dataset directory and the manifest files are found here:
```bash
# dataset directory
/mnt/d/datasets/audioset-2022-07-21
# manifest file
/mnt/d/datasets/audioset-2022-07-21/balanced_train_segments/manifest.json
```
However, I mapped the dataset directory as a volume this way:
```yaml
volumes:
    - /mnt/d/datasets/audioset-2022-07-21:/dataset
```
So, in my configs file, the path to my manifest file will be:
```yaml
train_manifest_path: /dataset/balanced_train_segments/manifest.json
```
You can also edit the configs in the other components as you see fit. Most importantly, make sure that inside `main.yaml`, your defaults are pointing to the right config for each component.

### 3. Run experiment!
```bash
cd build
docker-compose up
```
You can view your experiment logs via tensorboard as it runs here: http://localhost:6006/

If you wish to see the progress bar of each epoch, I suggest running the docker container in execution mode as such:
```bash
docker-compose run train_model bash
# inside the container
cd /walnet
python3 train.py
```

## Reference
```
@article{shah2018closer,
title={A Closer Look at Weak Label Learning for Audio Events},
author={Shah, Ankit and Kumar, Anurag and Hauptmann, Alexander G and Raj, Bhiksha},
journal={arXiv preprint arXiv:1804.09288},
year={2018}
}
```