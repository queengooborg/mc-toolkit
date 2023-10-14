# EssentialsX to BossShopPro
Convert an EssentialsX worth.yml to an item shop usable by BossShopPro (Minecraft Spigot plugins)

This program takes a decompiled version of Minecraft and creates an ordered list of all the blocks and their designated tabs.  After that, by taking an [EssentialsX](https://www.spigotmc.org/resources/essentialsx.9089/) worth.yml, generates an item shop for [BossShopPro](https://www.spigotmc.org/resources/bossshoppro-the-most-powerful-chest-gui-shop-menu-plugin.222/) + [BS-ItemShops](https://www.spigotmc.org/resources/itemshops-bsp-create-fancy-gui-shops-with-minimal-effort.26640/) on Bukkit/Spigot/Paperclip servers.

Developed and tested for 1.14 through 1.20. (Note: 1.20 implementation is currently experimental)

*Need a worth.yml with all the new items?  Check out my fork of [X00LA's file](https://github.com/X00LA/Bukkit-Essentials-worth.yml)!  https://gist.github.com/queengooborg/92d08120f0d6d25175f6c7a30e3ccac7*

## Requirements
 - Java 8+
 - Python 3.7+
 - PyYAML (`pip install pyyaml`)
 - [`DecompilerMC`](https://github.com/hube12/DecompilerMC) (added as a submodule)
 
## Usage

```sh
python3 generate_shops.py [mc_version]
```
