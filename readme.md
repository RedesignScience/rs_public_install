

# RS_PUBLIC_INSTALL


A package to help install Redesign Science's toolkit for a first time user.
 
Pre-requisites:

  1. access to our private R_S github repo
  2. obtained AWS keys from our DevOps team

The installation will attempt to download, install and then run our internal installer [rs_install](https://github.com/RedesignScience/rs_install). The rs_install installer will:

  1. install conda
  2. create an `rs` conda environment
  3. download & install packages and their dependencies
  4. download and install key configuration files


## Mac

If running on an Apple Silicon machine (eg. M1/M2), [Rosetta](https://support.apple.com/en-us/HT211861) is required to install dependencies that currently only have builds for x86 architecture. Rosetta can be installed via the following command:

    softwareupdate --install-rosetta

Go to the directory in which you want to store the packages. Then run:
  
    python -c "$(curl -fsSL https://raw.githubusercontent.com/RedesignScience/rs_public_install/main/rs_public_install.py)"
    
This will download Redesign's Python modules using the latest rs_install version to a `rs` folder within the current directory and install them to the `rs` conda environment. You can modify the code in the `rs` folder and it will modify the modules which are run from within the `rs` environment.

If you need to install Conda, once the script has installed Conda, it will stop.

This is to allow you to restart the terminal with special Conda environments.

Then you should go back the directory and rerun the script to continue.


## Ubuntu

As a prerequisite for the Ubuntu install script, make sure you have a public key registered under your GitHub account, and that either you are working from a SSH text session with SSH agent forwarding enabled or you have the private key stored locally - [detailed instructions](https://www.notion.so/redesignscience/SSH-Public-Key-Authentication-f560ff1c9942418180bd4aceb7fee77f).

Go to the directory in which you want to store the packages. Then, to run with defaults:
  
    python -c "$(wget --output-document -  https://raw.githubusercontent.com/RedesignScience/rs_public_install/main/rs_public_install.py)"

If you need to install Conda, once the script has installed Conda, it will stop.

This is to allow you to restart the terminal with special Conda environments.

Then you should go back the directory and rerun the script to continue.


