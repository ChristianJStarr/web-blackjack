




export function createElement(element_type, className='') {
    const element = document.createElement(element_type);
    element.className = className;
    return element;
}
