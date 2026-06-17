{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.gcc
    pkgs.stdenv.cc.cc.lib
  ];
}
