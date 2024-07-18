# Galaxy Project tools module for downloading, uploading & browsing iRODS/YODA


```TODO
TO DO:
+ build container, add to repo & describe
+ describe ibridges subfolder (Conda)
+ describe how tools work
```



__Galaxy iBridges download__ is a Galaxy tool that facilitates downloading of objects (files) and collections (folders) from iRODS/YODA, and can be integrated in a Galaxy workflow.

__Galaxy iBridges upload__ is a Galaxy tool that facilitates uploading of objects and collections to iRODS/YODA, and can be integrated in a Galaxy workflow.

__Galaxy iBridges browse__ is an interactive Galaxy tool that makes it possible to browse through an iRODS/YODA instance to locate objects and collections, and select them for use in a Galaxy workflow.

The tools are named for [iBridges](https://github.com/UtrechtUniversity/iBridges), the client used for interaction with iRODS/YODA.

## Installing tools files
Check out this repo and symlink the `src` folder to a link called `ibridges` under the `tools` folder of a Galaxy installation (or create a folder `tools/ibridges` and copy the contents of `src` into it).

## YODA environment
Copy the appropriate server configuration from the section Step [2. Configuring iCommands](https://www.uu.nl/en/research/yoda/guide-to-yoda/i-am-using-yoda/using-icommands-for-large-datasets#paragraph-152527) on the _Using iCommands for large datasets_ page, paste it into a file, and save it as `irods_environment.json` in the `tools/ibridges` folder. Leave the iRODS username `exampleuser@uu.nl` as it is.

## Galaxy configuration
### Changes to `user_preferences_extra_conf.yml`
Add the following to `config/user_preferences_extra_conf.yml` (create the file if it doesn't exist):

```yml
preferences:
    irods_yoda:
        description: Your YODA account
        inputs:
            - name: username
              label: Username
              type: text
              required: True
            - name: password
              label: Password
              type: secret
              required: True
```
This will create a section `Your YODA account` with inputs for _username_ and _password_ in the Galaxy user profile (Main menu: _User_ > _Preferences_; _Manage information_) in which users can store their credentials for accessing the appropriate iRODS/YODA instance. 

### Changes to `tool_conf.xml`
Add the tools to an appropriate section in the `config/tool_conf.xml`:
```xml
    <tool file="ibridges/ibridges_download.xml" />
    <tool file="ibridges/ibridges_upload.xml" />
    <tool file="ibridges/ibridges_browse.xml" />
```

**Please note: if you always up- and download to and from to the same, known paths, you may not need the browse function. In that case, omit the third line shown above, and skip the changes to `config/galaxy.yml` and `config/job.yml` detailed below.**

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

## Multiple iRODS/YODA instances in one Galaxy project

Currenly the tools work with one iRODS/YODA instance only. If you require accessing multiple instances within the same Galaxy project:
+ Create an extra set of tools for each instance (for instance: `tools/ibridges_geo/`, `tools/ibridges_gdk/`) and copy the contents of this repo's `src` folder into each.
+ Give each its own `irods_environment.json` for the correct server.
+ Create extra sections in the `user_preferences_extra_conf.yml` for the credentials for each server (or just passwords, if they the username is the same on all instances).
+ In each of the XML-files, change the string `irods_yoda` in the lines `$__user__.extra_preferences.get('irods_yoda|username', '')` and `$__user__.extra_preferences.get('irods_yoda|password', '')` to the matching section name in the preferences file.

## License

This project is licensed under the terms of the [MIT License](/LICENSE).
