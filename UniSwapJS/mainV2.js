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
async function getPrice(factory, amtIn, tradeDirection, token0Addy, token0Decimals, token0Symbol, token1Addy, token1Decimals, token1Symbol){

    const ABI = [
        // Some details about the token
        "function token0() external view returns (address)",
        "function token1() external view returns (address)",
        "function fee() external view returns (uint24)",
        "function decimals() view returns (uint)",
        
    ];
    const address = factory
    const poolContract = new ethers.Contract(address, ABI, provider);
    let token0Address = token0Addy//await poolContract.token0()
    let token1Address = token1Addy//await poolContract.token1()
    let tokenFee = await poolContract.fee()
    let inputTokenA = ""
    let inputDecimalsA = 0
    let inputTokenB = ""
    let inputDecimalsB = 0

    let tradeInfoArray = []
    if (tradeDirection == "baseToQuote") { tra
        inputTokenA = token0Addy
        const contractA = new ethers.Contract(inputTokenA, ABI, provider)
        inputDecimalsA = await contractA.decimals()
        inputTokenB = token1Addy
        const contractB = new ethers.Contract(inputTokenB, ABI, provider)
        inputDecimalsB = await contractB.decimals()
    }
    if (tradeDirection == "quoteToBase") {
        inputTokenA = token1Addy
        const contractA = new ethers.Contract(inputTokenA, ABI, provider)
        inputDecimalsA = await contractA.decimals()
        inputTokenB = token0Addy
        const contractB = new ethers.Contract(inputTokenB, ABI, provider)
        inputDecimalsB = await contractB.decimals()
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
        let token0Pair1Symbol = fileJsonArrayLimit[i].token0Trade1Symbol
        let token1Pair1Symbol = fileJsonArrayLimit[i].token1Trade1Symbol
        let token0Pair2Symbol = fileJsonArrayLimit[i].token0Trade2Symbol
        let token1Pair2Symbol = fileJsonArrayLimit[i].token1Trade2Symbol
        let token0Pair3Symbol = fileJsonArrayLimit[i].token0Trade3Symbol
        let token1Pair3Symbol = fileJsonArrayLimit[i].token1Trade3Symbol
        let token0Pair1Decimals = fileJsonArrayLimit[i].token0Trade1Decimals
        let token1Pair1Decimals = fileJsonArrayLimit[i].token1Trade1Decimals
        let token0Pair2Decimals = fileJsonArrayLimit[i].token0Trade2Decimals
        let token1Pair2Decimals = fileJsonArrayLimit[i].token1Trade2Decimals
        let token0Pair3Decimals = fileJsonArrayLimit[i].token0Trade3Decimals
        let token1Pair3Decimals = fileJsonArrayLimit[i].token1Trade3Decimals
        let token0Pair1Contract = fileJsonArrayLimit[i].token0Trade1Contract
        let token1Pair1Contract = fileJsonArrayLimit[i].token1Trade1Contract
        let token0Pair2Contract = fileJsonArrayLimit[i].token0Trade2Contract
        let token1Pair2Contract = fileJsonArrayLimit[i].token1Trade2Contract
        let token0Pair3Contract = fileJsonArrayLimit[i].token0Trade3Contract
        let token1Pair3Contract = fileJsonArrayLimit[i].token1Trade3Contract
        
    // console.log(fileJsonArrayLimit)

        
         //Trade 1 
        console.log("Checking trade 1 acquired coin...")
        let acquiredCoinT1 = await getPrice(pair1ContractAddress, amountIn, trade1Direction,token0Pair1Contract,token0Pair1Decimals,token0Pair1Symbol,token1Pair1Contract,token1Pair1Decimals,token1Pair1Symbol)
        // getLatestBlock()
        console.log(acquiredCoinT1)

        //Trade 2 
        console.log("Checking trade 2 acquired coin...")
        if (acquiredCoinT1 == 0) {return}
        let acquiredCoinT2 = await getPrice(pair2ContractAddress, acquiredCoinT1, trade2Direction, token0Pair2Contract,token0Pair2Decimals,token0Pair2Symbol,token1Pair2Contract,token1Pair2Decimals,token1Pair2Symbol)
        // getLatestBlock()
        // console.log(acquiredCoinT2)

        //Trade 3 
        console.log("Checking trade 3 acquired coin...")
        if (acquiredCoinT2 == 0) {return}
        let acquiredCoinT3 = await getPrice(pair3ContractAddress, acquiredCoinT2, trade3Direction, token0Pair3Contract,token0Pair3Decimals,token0Pair3Symbol,token1Pair3Contract,token1Pair3Decimals,token1Pair3Symbol)
        // getLatestBlock()
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

