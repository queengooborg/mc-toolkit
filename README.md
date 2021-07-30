# EssentialsXToBossShopPro
Convert an EssentialsX worth.yml to an item shop usable by BossShopPro (Minecraft Spigot plugins)

This program takes a decompiled version of Minecraft and creates an ordered list of all the blocks and their designated tabs.  After that, by taking an [EssentialsX](https://www.spigotmc.org/resources/essentialsx.9089/) worth.yml, generates an item shop for [BossShopPro](https://www.spigotmc.org/resources/bossshoppro-the-most-powerful-chest-gui-shop-menu-plugin.222/) + [BS-ItemShops](https://www.spigotmc.org/resources/itemshops-bsp-create-fancy-gui-shops-with-minimal-effort.26640/) on Bukkit/Spigot/Paperclip servers.

Developed and tested for 1.14 through 1.17.

## Requirements
 - Python 3.9 (earlier Python 3 versions may work but not recommended)
 - A Minecraft Forge MDK downloaded to your system
 - PyYAML (pip install pyyaml)
 
## Usage

```sh
python3 parse_items.py <forge_mdk_path>
```
