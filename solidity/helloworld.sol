pragma solidity ^0.5.11;

contract HelloWorld 
{
    address payable owner;
    string message = "hello world";
    
    function setMessage( string memory msg_ ) public
    {
        require( msg.sender == owner );
        message = msg_;
    }
    
    function getMessage() public view returns ( string memory )
    {
        return message;
    }
    
    constructor() public
    {
        owner = msg.sender;
    }
}