




export function createElement(element_type, className='') {
    const element = document.createElement(element_type);
    element.className = className;
    return element;
}

export function arraysEqual(arr1, arr2) {
    if (arr1.length !== arr2.length) return false;
    for (let i = 0; i < arr1.length; i++) {
        if (arr1[i] !== arr2[i]) return false;
    }
    return true;
}