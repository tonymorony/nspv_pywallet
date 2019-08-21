# nSPV pywallet

![alt text](https://i.imgur.com/VZhNf4r.png)

You can read about nSPV approach [here](https://medium.com/@jameslee777/nspv-a-simple-approach-to-superlight-clients-leveraging-notarizations-75d7ef5a37a9)

nSPV [cli reference](https://medium.com/@jameslee777/nspv-reference-cli-client-cf1ffdc03631)

## Dev installation:

Python3 required for execution:

*  `sudo apt-get install python3.6 python3-pip libgnutls28-dev libcurl4-openssl-dev libssl-dev python3-tk python3-ttkthemes`

pip packages needed:

* `pip3 install setuptools wheel slick-bitcoinrpc`

## Starting:  

* Put wallet files to same folder with komodod or put komodod to the same folder with wallet (komodod should support nSPV)

* Specify chain ticker as cli arg on start. For now KMD and ILN supported: 
`python3 main.py KMD` or `python3 main.py ILN`

If daemon wasn't started - wallet will start it for you. If daemon was started as nSPV superlight client - wallet should start fine as well.

Otherwise you'll need to stop daemon first then start wallet.
