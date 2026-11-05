#!/bin/bash
# Clone packages
git clone https://github.com/daeuniverse/openwrt-packages --single-branch --depth=1 clone/daepkg
git clone https://github.com/ophub/luci-app-amlogic --single-branch --depth=1 clone/amlogic
git clone https://github.com/Zerogiven-OpenWRT-Packages/luci-app-podman --single-branch --depth=1 feeds/luci/applications/luci-app-podman
# Argon 主题（第三方 feed，官方 OpenWrt 不自带）
git clone https://github.com/jerrykuku/luci-theme-argon --single-branch --depth=1 clone/argon
# Adjust packages
cp -rf clone/amlogic/luci-app-amlogic feeds/luci/applications/
cp -rf clone/daepkg/vmlinux-btf-builtin feeds/packages/net/
cp -rf clone/argon feeds/luci/themes/luci-theme-argon
sed -i '/luci-app-attendedsysupgrade/d' feeds/luci/collections/luci/Makefile
# Clean packages
rm -rf clone
