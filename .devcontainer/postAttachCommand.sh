#!/usr/bin/env bash

make install

sudo chown --recursive "$(id --user):$(id --group)" ~
sudo chmod --recursive 600 ~/.config/ngrok
sudo chmod --recursive u=rwX,g=,o= ~/.config/ngrok
