{
  description = "Randomized Linear Termination Tool";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/release-24.05";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  inputs.smtrat-release = {
    url = "https://github.com/ths-rwth/smtrat/releases/download/24.06/smtrat.tgz";
    type = "file";
    flake = false;
  };

  outputs = { self, nixpkgs, flake-utils, smtrat-release }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        smtrat = pkgs.stdenv.mkDerivation {
          name = "smtrat";
          src = smtrat-release;
          dontUnpack = true;
          installPhase = ''
            mkdir -p $out/bin
            cd $out/bin
            tar -zxvf $src smtrat-static
            mv smtrat-static smtrat
          '';
        };

        toolFiles = pkgs.stdenv.mkDerivation {
          name = "SiRop";
          src = pkgs.nix-gitignore.gitignoreSourcePure "!*.py" ./.;
          dontUnpack = true;
          propagatedBuildInputs = with pkgs; [ sage smtrat gnused ];
          installPhase = ''
            cd $src
            install -d $out/bin
            install -Dm755 *.py $out/bin
            substituteInPlace $out/bin/sirop.py --replace-fail 'default="smtrat"' 'default="${smtrat}/bin/smtrat"'
          '';
        };

        exampleFiles = pkgs.stdenv.mkDerivation {
          name = "sirop";
          src = pkgs.nix-gitignore.gitignoreSourcePure "!*.sage" ./examples;
          dontUnpack = true;
          installPhase = ''
            cd $src
            install -d $out/provided-examples
            install -Dm755 *.sage $out/provided-examples
          '';
        };
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [ sage smtrat ];
        };

        packages.default = toolFiles;

        packages.dockerImage = pkgs.dockerTools.buildImage {
          name = "sirop-docker";
          tag = "latest";

          copyToRoot = pkgs.buildEnv {
            name = "docker-root";
            pathsToLink = [ "/bin" "/provided-examples" ];
            paths = [ pkgs.coreutils pkgs.gnused toolFiles exampleFiles ];
          };

          runAsRoot = ''
            #!${pkgs.runtimeShell}
            mkdir -p /root
          '';

          config = {
            Entrypoint = [ "/bin/sirop.py" ];
            Env = [ "HOME=/root" ]; # otherwise sage complains
          };

          created = "now";
        };

        apps.default = {
          type = "app";
          program = "${toolFiles}/bin/sirop.py";
        };
      });
}
