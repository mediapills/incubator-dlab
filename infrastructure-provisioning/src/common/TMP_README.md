Install

```
$ pip install git+https://github.com/mediapills/incubator-dlab.git@DLAB-546#subdirectory=infrastructure-provisioning/src/common
```

**SSN Actions**

| ID | Action | Require | Implementation |
|----|--------|---------|----------------|
| 1  | Create DLab user
| 2	 | Install prerequisites
| 3	 | Create service directories	
| 4	 | Set hostname	
| 5	 | Install NGINX reverse proxy | 2
| 6	 | Configure SSL certificates	
| 7	 | Configure NGINX reverse proxy | 2, 4, 5, 6
| 8	 | Install Jenkins | 2
| 9	 | Configure Jenkins | 2, 8
| 10 | Copy SSH key	
| 11 | Copy backup scripts | 3
| 12 | Copy gitlab scripts | 3
| 13 | Ensure ciphers	
| 14 | Modify configuration file | 3
| 15 | Download toree | 3, 14
| 16 | Install docker | 2
| 17 | Build docker images | 2, 3, 14, 15, 16
| 18 | Copy DLab libs
| 19 | Install supervisor | 2
| 20 | Install database (MongoDB) | 2, 3?
| 21 | Configure database MongoDB | 2, 3?, 20
| 22 | Install build deps | 2
| 23 | Build UI | 2, 3, 14, 22
| 24 | Start UI | 2, 3, 14, 22, 23

