# WALNet
This is a re-implementation of the [official WALNet repository](https://github.com/ankitshah009/WALNet-Weak_Label_Analysis).

## New Things

- [x] [Hydra](https://hydra.cc/docs/intro/) to manage our pipeline configurations
- [x] [PyTorch Lightning](https://www.pytorchlightning.ai/) to abstract away tedious code, and enforce a standard experiment code structure
- [x] [yt-dlp](https://github.com/yt-dlp/yt-dlp) to manage the downloading of data from Youtube. It allows to only download the required segments of a video, rather than the entire video before processing, saving downloading duration by 50x
- [x] Reorganized the code for better readability
- [x] Allows loading data on-the-fly, instead of preprocessing all dataset features before training. This enables transformations on-the-fly later on for training more robust models

## TODOs

- [ ] Add logging features
- [ ] Documentation
