# openEO: OpenShift Driver (Reference back end used for the impact Evaluation)

## Information
- version: 0.3
- Python: 3.6.2
- Databases: Postgres, Redis
- Message Broker: RabbitMQ
- Dependencies: Flask, Nameko

The openEO OpenShift driver provides openEO API functionality on top of RedHat's OpenShift Origin.
A flask REST client on route /jobs is provided.

For more information on OpenShift please visit:
- [OpenShift Origin website](https://www.openshift.org/)
- [OpenShift Origin documentation](https://docs.openshift.org/latest/welcome/index.html)
- [How to setup an OpenShift cluster](https://docs.openshift.org/latest/install_config/install/planning.html)

# Installation
## Local openShift cluster

For testing purposes, it may be convenient to install a local openShift cluster (which fully runs on a single machine) and deploy a (number of) project(s) on it.
The following documentation explains how to install oc client tools, oc-cluster wrapper and configure a mock-up of the EODC openEO back-end on a laptop. Insructions here are taken partly from this link (https://opensource.com/article/18/11/local-okd-cluster-linux), but they are tailored to Ubuntu 18.04 and to our openEO deployment, including creating persistent volumes and persistent volume claims.

These are the different steps:

- **oc client tools**
- **oc-cluster wrapper**
- **openEO services**
- **openEO execution environment**

**oc client tools**

With the latest oc client tools version (v3.11) there are connectivity issues from the pods within the cluster when trying to pull images online (or in general to access internet). Until this is solved, we use v3.9:

```
cd ~/Downloads
wget https://github.com/openshift/origin/releases/download/v3.9.0/openshift-origin-client-tools-v3.9.0-191fece-linux-64bit.tar.gz
tar -xzvf openshift-origin-client-tools-v3.9.0-191fece-linux-64bit.tar.gz
```
Optionally, place the executable in your $PATH, e.g.:

`sudo cp openshift-origin-client-tools-v3.9.0-191fece-linux-64bit/oc /usr/local/bin/`

Check that it works:
```
$ oc version
oc v3.9.0+191fece
kubernetes v1.9.1+a0ce1bc657
features: Basic-Auth GSSAPI Kerberos SPNEGO
```

At this point you can fire up a local cluster simply by running:

`oc cluster up`

However, the cluster will not be persistent, hence the need of oc-cluster wrapper.


**oc-cluster wrapper**

oc-cluster wrapper provides, amongst other things, cluster persistency and cluster profiles, i.e. the ability to set up a number of different clusters, each of which can contain a number of projects. Note that you can only run one cluster profile at any given time. For our purposes, it is mostly the convenience of having a persistent cluster that we want to achieve. Have a quick look on their github page (https://github.com/openshift-evangelists/oc-cluster-wrapper), particularly under 'Cluster profiles'.

Clone the repository

```
git clone https://github.com/openshift-evangelists/oc-cluster-wrapper
echo 'PATH=$HOME/oc-cluster-wrapper:$PATH' >> $HOME/.bash_profile
echo 'export PATH' >> $HOME/.bash_profile
```

Generally, you can now use oc-cluster instead of oc cluster. Use the first when creating a cluster to use the wrapper we just installed.

Create and start a local cluster on your localhost

`oc-cluster up myclustername --routingsuffix 127.0.0.1.nip.io`

The nip.io suffix is needed for the EODC openEO instance, not for openShift itself. Do not use xip.io instead of nip.io, as xip.io will not work on localhost.

You will find a folder named myclustername under the profiles of oc-cluster wrapper, here:

`ls $HOME/.oc/profiles/`

By default on the cluster you have a normal user (developer/developer) and an admin user (admin/admin). To check that your cluster is running, simply open the browser on https://127.0.0.1/8443, or type:

`oc-cluster status`

You can stop a cluster with:

`oc-cluster down`

You can list all the clusters you have created with:

`oc-cluster list`

You can delete a cluster with:

`oc-cluster destroy`

To test that the basic installation works, create this sample app:

```
oc new-app php:5.6~https://github.com/rgerardi/ocp-smoke-test.git
oc expose svc ocp-smoke-test
```

You might have to login to do that (oc login -> developer/developer). If the app is installed and the route works (i.e. you can click on it), you are good to go.


**openEO services**

  We are going to install, in this order, the following processes: rabbitmq, gateway, data, processes (includes process_graphs), jobs. Each of these has a yaml template, stored in the templates folder in this repository. These templates pull code from the master branch on this github repository.

  Create a new project from the web console with the name you prefer. Make sure you are in the scope of that project from the command line: `oc project myprojectname`

  You can see all the projects with: `oc projects`


  - rabbitmq

      `oc process -f rabbitmq.eodc.yaml | oc create -f -`

      You will see a rabbitmq app/service on your web console inside myprojectname.

  - gateway

      `oc process -f gateway_local.eodc.yaml | oc create -f -`

      The differences between the local and 'original' gateway are the fields 'GATEWAY URL' and 'CLIENT JSON'. Once the service is up, you should be able to display the capabilities of openEO at the url http://openeo.local.127.0.0.1.nip.io


  - data

      `oc process -f data.eodc.yaml | oc create -f -`

      Once this is up, try listing the available datasets/collections at http://openeo.local.127.0.0.1.nip.io/collections

  - processes (and process_graphs)

      This service includes a psql pod. In order to avoid data loss, it mounts a persistent volume claim (pvc), which depends on a persistent volume (pv). For openShift, a pv is a resource (like CPU and memory), and hence must be created in advance (with admin rights), while a pvc is an allocation of (volume) resources and can be done by a user when creating a service. The pvc is specified in the processes template, but we need to create the pv first. Inside the 'persistent_volume_processes.yaml' file, modify 'the-cluster-name' with the name of the cluster you created, then run:

      `oc create -f persistent_volume_processes.yaml`

      The mount folder specified in the yaml file must have full right for user and group, run the following to achieve this:

      `sudo chmod 770 -R $HOME/.oc/profiles/the-cluster-name/pv`

      where 'the-cluster-name' must be adapted to the name you used. You can see all pv on your cluster by running (with admin rights, i.e. oc login -> admin/admin): `oc get pv`

      A number of pv are automatically created by openShift when generating the cluster, plus there should be one named 'vol-openeo-processes'.

      Now you can create the processes service:

      `oc process -f processes.eodc.yaml | oc create -f -`

      You will see that the project now has a pvc with: `oc get pvc` and/or under the storage tab on the web console (no admin rights needed for this, but make sure you are in the right project.)

  - jobs

    As for the processes service, create the pv with the file 'persistent_volume_jobs.yaml' (modify the cluster name first), then create the service with:

    `oc process -f jobs.eodc.yaml | oc create -f -`

    Remember to also 'chmod' the mounted folder as in the processes step.

  - initialize psql databases (processes and jobs services)

    The databases are created empty (no tables, no data) and they must be initialized (only when creating the services the first time). For the processes service, from the web console, go to Applications/Pods/openeo-processes-1-xxxxx (not the db and not the build), then select Terminal. From the CLI, type:

    `alembic upgrade head`

    To double check that this worked, connect now to the openeo-processes-db-1-xxxxx pod, go to the terminal, and type:

    `psql processes`

    `\d`

    You should see the schema of the different tables inside the processes database (perhaps unclearly, the processes database contains a processes table...)

    Another way to connect to the pod is to start a terminal, get a list of the running pods (`oc get pods` , you must be in the right project), then remote-shell to the pod:

    `oc rsh openeo-processes-1-xxxxx`

    From here you can type commands above. Do the same for the jobs service.

  - add processes to the processes databases

    openEO processes currently must be added manually. You can use POSTMAN and submit a json file (raw/json), like on item in this list of processes (https://github.com/bgoesswein/dataid_openeo/blob/master/openeo-openshift-driver/processes.json). For example, to add the NDVI process, make sure your cluster is up and that the processes service is properly initialized (including the pv, pvc and database initialized), then from POSTMAN send a POST request to the proper endpoint (http://openeo.local.127.0.0.1.nip.io/processes), including the following under Body/raw (json):

        {
          "name": "NDVI",
          "summary": "Calculates the Normalized Difference Vegetation Index.",
          "description": "Calculates the Normalized Difference Vegetation Index.",
          "parameters": {
            "imagery": {
              "description": "EO data to process.",
              "required": true,
              "schema": {
                "type": "object",
                "format": "eodata"
              }
            },
            "red": {
              "description": "Band id of the red band.",
              "required": true,
              "schema": {
                "type": "string"
              }
            },
            "nir": {
              "description": "Band id of the near-infrared band.",
              "required": true,
              "schema": {
                "type": "string"
              }
            }
          },
          "returns": {
            "description": "Processed EO data.",
            "schema": {
              "type": "object",
              "format": "eodata"
            }
          },
          "exceptions": {
            "RedBandInvalid": {
              "description": "The specified red band is not available or contains invalid data."
            },
            "NirBandInvalid": {
              "description": "The specified nir band is not available or contains invalid data."
            }
          }
        }
        
If it worked fine, send a GET request to the same url to display the process (or alternatively navigate to http://openeo.local.127.0.0.1.nip.io/processes with your browser).

After that all filter processes type need to be set to "filter" manually. Therefore connect to the POD of the processes-db via the web interface of Openshift, connect to the database with "psql processes" and update the "p_type" all records with "filter" in the beginning and "get_collection" to the value "filter".
