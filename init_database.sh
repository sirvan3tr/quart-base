#! /usr/bin/env sh

quart recreate_db
quart setup_dev
quart add_fake_data