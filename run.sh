#!/usr/bin/env sh
/home/bibinuz/.local/share/PrismLauncher/java/java-runtime-delta/bin/java -XX:+UseZGC -XX:+ZGenerational @user_jvm_args.txt @libraries/net/neoforged/neoforge/21.1.233/unix_args.txt "$@"

