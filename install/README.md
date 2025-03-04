# application packaging

This document describes the main alternatives for packing tools that were
considered for the webtool, for the purpose of distributing the application to
end-users so that they may run it themselves in a user-friendly way.

The main alternatives considered were pyinstaller and cx_freeze. Pyoxidizer may
also have been good, but wasn't explored fully due to a higher barrier of
entry.

All the tools considered were cross-platform, however, none were able to
cross-compile, meaning that the app could only be packaged for platform X on
platform X.

We chose **cxFreeze** as our packaging tool due to it being simpler, faster and
more versatile, as shown below.

## pyinstaller

- build time: 73s
- uncompressed archive size: ~280MB
- binary distributable size: ~120MB
- works without any code change

binary distribution types:
- single-file self-extracting archive

## cx_freeze

- build time: 37s
- uncompressed archive size: ~330MB
- binary distributable size: ~70MB (linux appimage)
- requires a tiny code change (to get paths working)

binary distribution types:
- linux:
    - appimage
    - deb
    - rpm
- windows:
    - msi
- mac:
    - app
    - dmg
