## Slack remind all ansible provisioning&testing

##### please note: provisioned service is exposed via http on a container's port, so need a SSL terminating proxy to function best

### Provisioning via ansible-playbook

* dist playbook
  ```
  cp provision.dist.yml provision.yml
  ```
* (also if using local inventory dist it) 
  ```
  cp inventory.dist -> inventory
  ```
* update authorization token and signing key in the `provision.yml`
* update server IP in the `inventory`
* run
    ```
    ansible-playbook provision.yml -i inventory
    ```
    
### Provisioning via molecule

disclaimer: our main container-providing tool is `lxc/lxd` and so is the molecule setup,
but feel free to `dockerize` the app and do PR if you need it
* create virtualenv for molecule (python3.6+ recommended) and `source` into it
* install dependencies:
```
pip install molecule
```
* then
```
cp molecule/dist/playbook.dist.yml molecule/dist/playbook.yml

```
* update tokens and oauth keys
* provision:
```
molecule create --scenario-name=dist && molecule converge --scenario-name=dist
```
* or if you've installed lxd via snap:
```
molecule create --scenario-name=dist-snap && molecule converge --scenario-name=dist-snap
```
        
### Testing via molecule

* create virtualenv for molecule (python3.6+ recommended) and `source` into it
* then
```
pip install molecule
molecule test
```    