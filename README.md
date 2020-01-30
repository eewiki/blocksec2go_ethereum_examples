# BlockSec2Go Ethereum Examples

This repository contains the Python files used to demonstrate how to use Infineon's Blockchain Security 2Go starter kit
(and their blocksec2go Python library) with Ethereum. The eewiki article
[Using Infineon's Blockchain Security 2Go Starter Kit with Ethereum](https://www.digikey.com/eewiki/display/Motley/Using+Infineon%27s+Blockchain+Security+2Go+Starter+Kit+with+Ethereum)
provides detailed explainations of how to create Ethereum accounts with a Security 2Go card and use those accounts to recieve/send ether, create
smart contracts, and invoke smart contract functions. 

# Prerequisites 

## Create a private Ethereum blockchain

Use the puppeth tool to create a genesis block and initialize two or more nodes with this block. Create at least one account on the node 
which you will connect (port 8501). Use geth to start your nodes and connect them. 

Complete details in the eewiki article.

## Install Python libraries

To run the examples, you will have to install the following python modules: **web3** and **blocksec2go**. 
Note that blocksec2go requires swig be installed (see [Infineon's Blockchain Security 2Go Library repository](https://github.com/Infineon/BlockchainSecurity2Go-Python-Library) for details).

# Contact the Author
If you have any other questions/feedback about this code or the accompanying eewiki article,
feel free to send an email to [eewiki@digikey.com](mailto:eewiki@digikey.com) 
or visit Digi-Key's [TechForum](https://forum.digikey.com/c/eewiki-discussions).
