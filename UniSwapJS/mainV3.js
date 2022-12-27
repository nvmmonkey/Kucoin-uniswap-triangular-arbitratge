const ethers = require('ethers');
const provider = new ethers.providers.JsonRpcProvider("https://mainnet.infura.io/v3/50ba464df68f4d93b5cc4ada60fbfd95");
const QuoterABI = require('/Users/apple/Desktop/development/Pycharm/Triarb/UniSwapJS/node_modules/@uniswap/v3-periphery/artifacts/contracts/lens/Quoter.sol/Quoter.json').abi;

//read file //////////////
function getFile(fPath) {
    const fs = require('fs')
    try{
        const data = fs.readFileSync(fPath, 'utf-8')
        return data
    }catch(err){
        return[]
    }
}

//Calculate Arbitrage //////////////
function calculateArbitrage(amountIn, amountOut, surfaceObj){
    
    //Calculate profit loss
    let threshold = 0
    let resultArray = [surfaceObj]
    let profitLoss = amountOut - amountIn
    let profitLossPerc = 0
    if (profitLoss > threshold) {
        profitLossPerc = profitLoss * 100 / amountIn
        
        //provide Output Result
        resultArray.push({profitLossPerc: profitLossPerc})
        console.log(resultArray)

    }
    return 

}



//get prices //////////////
async function getPrice(factory, amtIn, tradeDirection){

    const ABI = [
        // Some details about the token
        "function token0() external view returns (address)",
        "function token1() external view returns (address)",
        "function fee() external view returns (uint24)",
        
    ];
    const address = factory
    const poolContract = new ethers.Contract(address, ABI, provider);
    let token0Address = await poolContract.token0()
    let token1Address = await poolContract.token1()
    let tokenFee = await poolContract.fee()
    
    //Get individual token information{symbol, Name, Decimals}
    let addressArray = [token0Address, token1Address]
    let tokenInfoArray = []
    for (let i=0; i<addressArray.length; i++){
        let tokenAddress = addressArray[i]
        let tokenABI = [
            "function name() view returns (string)",
            "function symbol() view returns (string)",
            "function decimals() view returns (uint)",
        ]
        let contract = new ethers.Contract(tokenAddress, tokenABI, provider)
        let tokenSymbol = await contract.symbol()
        let tokenName = await contract.name()
        let tokenDecimals = await contract.decimals()

        let obj = {
            id: "token" + i,
            tokenSymbol: tokenSymbol,
            tokenName: tokenName,
            tokenDecimals: tokenDecimals,
            tokenAddress: tokenAddress
        }
        tokenInfoArray.push(obj)
        console.log(obj)
    }
    //identified the correct token to input as A and B respiectively
    let inputTokenA = ""
    let inputDecimalsA = 0
    let inputTokenB = ""
    let inputDecimalsB = 0
    if (tradeDirection == "baseToQuote"){
        inputTokenA = tokenInfoArray[0].tokenAddress
        inputDecimalsA = tokenInfoArray[0].tokenDecimals
        inputTokenB = tokenInfoArray[1].tokenAddress
        inputDecimalsB = tokenInfoArray[1].tokenDecimals
    }
    if (tradeDirection == "quoteToBase"){
        inputTokenA = tokenInfoArray[1].tokenAddress
        inputDecimalsA = tokenInfoArray[1].tokenDecimals
        inputTokenB = tokenInfoArray[0].tokenAddress
        inputDecimalsB = tokenInfoArray[0].tokenDecimals
    }

    //Reformat Amount In
    if (!isNaN(amtIn)) {amtIn = amtIn.toString()}
    let amountIn = ethers.utils.parseUnits(amtIn, inputDecimalsA).toString()
    
    //Get Uniswap V3 Quote
    const quoterAddress = "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6";
    const quoterContract = new ethers.Contract(quoterAddress, QuoterABI, provider)
    let quotedAmountOut = 0
    try {
        quotedAmountOut = await quoterContract.callStatic.quoteExactInputSingle(
            inputTokenA,
            inputTokenB,
            tokenFee,
            amountIn,
            0
        )
    }catch (err){
        return 0
    }
    
    //Format Output
    let outputAmount = ethers.utils.formatUnits(quotedAmountOut, inputDecimalsB)
    return outputAmount


}


//get lastest block //////////////
async function getLatestBlock() {
    const blockNumber = await provider.getBlockNumber();
    console.log('Latest block:', blockNumber);
}

getLatestBlock();


//get depth //////////////
async function getDepth(amountIn){
    
    //get JSON surface rate
    console.log(">>>>>> Reading Surface Rate Info... >>>>>>>")
    let fileInfo = getFile("../UniSwap/uniswap_surface_rate.json");
    fileJsonArray = JSON.parse(fileInfo)
    let limit = fileJsonArray.length
    fileJsonArrayLimit = fileJsonArray.slice(0, limit)
    // console.log(fileJsonArrayLimit)
    
    //Loop throught each trade and get Price information
    for (let i=0; i<fileJsonArrayLimit.length; i++) {
        
        //Extract variables
        let pair1ContractAddress = fileJsonArrayLimit[i].poolContract1
        let pair2ContractAddress = fileJsonArrayLimit[i].poolContract2
        let pair3ContractAddress = fileJsonArrayLimit[i].poolContract3
        let trade1Direction = fileJsonArrayLimit[i].poolDirectionTrade1
        let trade2Direction = fileJsonArrayLimit[i].poolDirectionTrade2
        let trade3Direction = fileJsonArrayLimit[i].poolDirectionTrade3

        
         //Trade 1 
        console.log("Checking trade 1 acquired coin...")
        let acquiredCoinT1 = await getPrice(pair1ContractAddress, amountIn, trade1Direction)
        getLatestBlock()
        console.log(acquiredCoinT1)

        //Trade 2 
        console.log("Checking trade 2 acquired coin...")
        if (acquiredCoinT1 == 0) {return}
        let acquiredCoinT2 = await getPrice(pair2ContractAddress, acquiredCoinT1, trade2Direction)
        getLatestBlock()
        console.log(acquiredCoinT2)

        //Trade 3 
        console.log("Checking trade 3 acquired coin...")
        if (acquiredCoinT2 == 0) {return}
        let acquiredCoinT3 = await getPrice(pair3ContractAddress, acquiredCoinT2, trade3Direction)
        getLatestBlock()
        console.log(acquiredCoinT3)

        //Calculate and Show results
        let result = calculateArbitrage(amountIn, acquiredCoinT3, fileJsonArrayLimit[i])
        
        // Provide output result
        
    }
    return

    
}


//           //
// MAIN PANEL//
//          //
getDepth(amountIn=1)

