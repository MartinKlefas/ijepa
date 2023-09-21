#!/bin/sh
python -u check_images.py --fname configs/kf_crypts_vith14_ep300.yaml
python -u main.py --fname configs/kf_crypts_vith14_ep300.yaml --devices cuda:0