# Galaxy Project tools module for downloading from, uploading to, and browsing iRODS

__iBridges download from iRODS__ is a Galaxy tool that facilitates downloading of objects (files) and collections (folders) from iRODS.

__iBridges upload to iRODS__ is a Galaxy tool that facilitates uploading Galaxy files and collections to iRODS.

__iBridges browser for iRODS__ is an interactive Galaxy tool that allows users to browse through an iRODS instance to locate objects and collections, and select them for use in a Galaxy workflow.

The tools are named for [iBridges](https://github.com/UtrechtUniversity/iBridges), the client used for interaction with iRODS.

## What it does
### iBridges download from iRODS
Tool for downloading files and folders from iRODS into a Galaxy collection. Takes paths to one or more files (dataobjects), one or more folders (collections), or a combination, and downloads all files into the same Galaxy collection.

### iBridges upload to iRODS
Tool for uploading files or collections from Galaxy into an iRODS folder.

### iBridges browser for iRODS
iBridges browser launches as a [Galaxy Interactive Tool](https://training.galaxyproject.org/training-material/topics/admin/tutorials/interactive-tools/tutorial.html) that allows the user to browse the objects and collections in the iRODS instance through a web interface.

## Installation
The three tools are available in the Galaxy Toolshed as a single module called 'ibridges' ([Toolshed link](https://toolshed.g2.bx.psu.edu/repository?repository_id=3976454f355048d6)), and can be installed in a running Galaxy instance via _Admin > Tool Management > Install and Uninstall_ (search for 'ibridges').

Currenly the tools can work with only one iRODS instance per installation. 

## Galaxy configuration
### Changes to `user_preferences_extra_conf.yml`
Add the following to `config/user_preferences_extra_conf.yml` (create the file if it doesn't exist):

```yml
preferences:
    irods_config:
        description: Your iRODS account
        inputs:
            - name: username
              label: Username
              type: text
              required: True
            - name: password
              label: Data Access Password
              type: secret
              required: True
            - name: env
              label: Config
              required: True
              type: text
```

This will create a section `Your iRODS account` with inputs for _Username_, _Data Access Password_, and _Config_ in the Galaxy user profile, in which users can store their credentials for accessing the appropriate iRODS instance. 

<span style="color:red">**Please note: if you don't need the browse function, you can skip the changes to `config/galaxy.yml` and `config/job.yml` below.**</span>

### Changes to `galaxy.yml`
The browse tool is an interactive tool (essentially a webserver communicating with the iRODS server, running in a Docker container). To enable the running of interactive tools, make sure the following settings are present in the  `galaxy` and `gravity` sections of `config/galaxy.yml` (change `my_galaxy_domain.com` to the domain of the actual Galaxy server):

```yml
galaxy:
  interactivetools_enable: true
  outputs_to_working_directory: true
  galaxy_infrastructure_url: http://my_galaxy_domain.com:8080
  interactivetools_map: database/interactivetools_map.sqlite
  interactivetools_upstream_proxy: false
  interactivetools_proxy_host: localhost:4002

gravity:
  gx_it_proxy:
    enable: true
    port: 4002
```

### Changes to `job.yml`
For the running of interactive jobs, add the following to the `config/job.yml` file (create the file if it doesn't exist):

```yml
runners:
  local:
    load: galaxy.jobs.runners.local:LocalJobRunner
    workers: 4

execution:
  default: docker_dispatch
  environments:
    local:
      runner: local

    docker_local:
      runner: local
      docker_enabled: true
      docker_set_user:

    docker_dispatch:
      runner: dynamic
      type: docker_dispatch
      docker_destination_id: docker_local
      default_destination_id: local
```

## iRODS environment file
Copy the appropriate server configuration from the section [Step 2. Configuring iCommands](https://www.uu.nl/en/research/yoda/guide-to-yoda/i-am-using-yoda/using-icommands-for-large-datasets#paragraph-152527) of the page 'Using iCommands for large datasets', and paste it as a string into the _Config_ input for `Your iRODS account` (via main Galaxy menu: _User_ > _Preferences_; link _Manage Information_). You can leave the iRODS username `exampleuser@uu.nl` as it is.

## iRODS access 
Make sure users using the tools have access to the iRODS instance specified in the iRODS environment Users must save their username (e-mail address) and Data Access Password in the appropriate inputs for `Your iRODS account`. Every time one of the tools needs to access iRODS, it automatically reads the credentials from the user's personal profile, and uses them to log in. Be aware that Data Access Passwords have a limited lifespan; if a DAP has expired, the tools will fail, and you will see an error message in the error output.

## Running the iBridges browser for iRODS
When running an interactive tool, the interactive tool-icon (three gears) will appear in the Galaxy main menu, to the right of _User_. Clicking the icon opens a screen listing the interactive tools that are running. This can also be reached using the option _Active Interactive Tools_ in the _User_-item of the main menu. If the icon and the option in the User-menu aren't there, it means no interactive tools are running. If they appear briefly and then disappear, launching of the tool was unsuccesful.

Next, open the tool by clicking 'ibridges browser' in the Active Interactive Tools-list (if the link isn't clickable, the tool is still starting). A new tab will open with a simple web page listing the dataobjects and collections in the user's home folder for the iRODS instance. Navigate through the instance by clicking collections' names, and the links in the breadcrumb path.

To select a path as output for the module, navigate to the appropriate collection and click the 'select'-button. The interactive tool will terminate, signalling to Galaxy that exectution of the workflow can continue. The selected path will be available as the module output parameter 'iRODS path' (this will take a few seconds).
Alternatively, you can also copy the path without quitting to your computer's clipboard by clicking 'copy'.
To quit without selecting a path, click 'quit' or close the page; the value of the 'iRODS path' parameter will be None.

Please note that the tools' web page cannot close itself; close it by hand once you're done.

## Building a local copy of the browser container
Galaxy iBridges browse uses a Docker container which runs in Galaxy's own Docker-environment. It can be pulled from [Utrecht University's package registry](https://github.com/UtrechtUniversity/galaxy-tools-ibridges/pkgs/container/ibridges_browse), and is pulled automatically by Galaxy, from the specification in `ibridges_browse.xml`:

```xml
    [...]
    <requirements>
        <container type="docker">ghcr.io/utrechtuniversity/ibridges_browse:0.1</container>
    </requirements>
    [...]
```

If for some reason you want to build your own version of the container, the Dockerfile is available in the [docker-src](docker-src) folder of this repo. Make sure to change the value in the 'container' element in `ibridges_browse.xml` to the appropriate value.

## License
This project is licensed under the terms of the [MIT License](/LICENSE).
