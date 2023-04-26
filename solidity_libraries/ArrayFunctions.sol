// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

library ArrayFunctions {
    function removeStringFromArray(
        uint256 index,
        string[] storage array
    ) public {
        if (index >= array.length) return;

        for (uint256 i = index; i < array.length - 1; i++) {
            array[i] = array[i + 1];
        }
        array.pop();
    }

    function removeAddrFromArray(
        uint256 index,
        address[] storage array
    ) public {
        if (index >= array.length) return;

        for (uint256 i = index; i < array.length - 1; i++) {
            array[i] = array[i + 1];
        }
        array.pop();
    }
}
