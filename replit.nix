{pkgs}: {
  deps = [
    pkgs.postgresql
    pkgs.openssl
    pkgs.libxcrypt
    pkgs.rustc
    pkgs.cargo
    pkgs.glibcLocales
    pkgs.cacert
    pkgs.libiconv
    pkgs.bash
    pkgs.pgadmin4
  ];
}
