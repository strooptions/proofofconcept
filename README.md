# proofofconcept
requires Python 2.7
see requirements.txt for other dependencies

run process.py in a python environment

currently running on the Stellar testnet with fake accounts, generated each time the program is run (except for the fake XRP seller)

run write() to see an option written

run see(systemdb) to see the state of the contract system, including:

- the option writer
- the writer's issuing account ("Printer"), which originates the OCA option contract asset, and two utility assets:
- - the SPA "stroop asset", required to create a minimum order size during the option exercising process
- - the GTA "gate asset", also involved in the above
- the writer's main contract account ("Contract"), which will be locked for the duration of the contract except for preauthorized transactions required for the option exercising process
- the writer's "Pipe" account, which remains under the writer's control for the duration of the contract, and into which the strike price is sent upon option exercise. This is in place so that the writer can close their position with the help of a lender, by buying an equivalent option token, sending it to the Pipe, and borrowing the underlying 
- the XRP distributor account ("XRPdis")

run exercise() to see someone (for simplicity's sake, the writer) exercise the option

exercise() will print snapshots of the contract system periodically during the process

if you plan to run the program again, run systemdb.purge() to clear the system database before closing the program

