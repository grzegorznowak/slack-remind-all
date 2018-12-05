## Slack remind all ansible provisioning&testing

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

* install dependencies:
```
pip install molecule
```
* then create your molecule scenario with your image settings
* provision:
```
molecule provision --scenario-name=[your-scenario-name]
```
        
### Testing via molecule

```
pip install molecule
molecule test
```    