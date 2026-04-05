{
  description = "Vybe URL shortener dev environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python313;
        pythonPkgs = python.pkgs;
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            python
            pkgs.uv

            # Frontend
            pkgs.nodejs_22
            pkgs.pnpm

            # Dev workflow
            pkgs.just
            pkgs.overmind
            pkgs.docker-compose

            # Useful tools
            pkgs.postgresql_16
          ];

          shellHook = ''
            echo "Vybe dev shell ready — Python ${python.version}, Bun, Node, docker-compose"
          '';
        };
      });
}
