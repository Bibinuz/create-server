#!/usr/bin/env sh
java -XX:+UseZGC -XX:+ZGenerational @user_jvm_args.txt @libraries/net/neoforged/neoforge/21.1.233/unix_args.txt "$@"

