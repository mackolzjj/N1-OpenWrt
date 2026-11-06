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
# ---- 简体中文语言包：补齐 feed 包 -------------------------------------------
# luci.mk 会扫描包目录下的 po/<BCP47>/*.po，自动生成 luci-i18n-<name>-zh-cn
# 包；.config 里的 CONFIG_LUCI_LANG_zh_Hans=y 负责把它们默认启用。
# 三个上游仓库都自带 po/zh_Hans，这里确保它们确实进了 feed（上游改目录结构或
# feeds update 清理时不会静默丢失）。
# 这是中文翻译的唯一路径：不下载官方 ipk，也不在构建期手工复制 .lmo。

ensure_zh_hans() {
    pkg="$1"; src="$2"
    if [ ! -d "$pkg/po/zh_Hans" ] && [ -n "$src" ] && [ -d "$src/po/zh_Hans" ]; then
        mkdir -p "$pkg/po"
        cp -rf "$src/po/zh_Hans" "$pkg/po/"
    fi
    if [ ! -d "$pkg/po/zh_Hans" ]; then
        echo "::warning:: $pkg 缺 po/zh_Hans，该插件中文包不会生成，请检查上游 po 目录结构"
    fi
}

ensure_zh_hans feeds/luci/applications/luci-app-amlogic clone/amlogic/luci-app-amlogic
ensure_zh_hans feeds/luci/applications/luci-app-podman  ""
ensure_zh_hans feeds/luci/themes/luci-theme-argon     clone/argon

echo "== zh_Hans 翻译源文件 =="
find feeds/luci/applications/luci-app-amlogic/po/zh_Hans \
     feeds/luci/applications/luci-app-podman/po/zh_Hans \
     feeds/luci/themes/luci-theme-argon/po/zh_Hans -name '*.po' -print 2>/dev/null || true

# Clean packages
rm -rf clone
