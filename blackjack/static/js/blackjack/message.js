import {createElement} from "./utility.js";

export class Message {

    constructor(table=null) {
        this.table = table;
        this.node = createElement('div', 'message');
        this.text_node = createElement('p', 'message__text');

        this.progress_node = createElement('div', 'message__progress');

        this.message = '';

        this.node.append(
            this.text_node,
            this.progress_node,
        )
    }


    update(state) {
        const message_time = state?.message_time ?? 0;
        let message;
        if(state?.result) {
            switch (state.result) {
                case 'win':
                    message = 'You Win';
                    break;
                case 'push':
                    message = 'You Push';
                    break;
                case 'lose':
                    message = 'You Lose';
                    break;
                default:
                    message = '';
            }
        }else {
            message = state?.message ?? '';
        }

        if (!(!message && this.temp_message) && message !== this.message) {
            this.setMessage(message, message_time);
        }

    }

    setTempMessage(message, time) {
        this.temp_message = message;
        this.setMessage(this.temp_message);

        this.temp_timeout = setTimeout(() => {
            if (this.temp_message === message) {
                this.temp_message = '';
                this.setMessage(this.message);
            }
        }, time);
    }

    setMessage(message, message_time=0) {
        if(!this.temp_message || message) {
            this.message = message;
            this.text_node.textContent = message;
            this.progress_node.style = `--progress: 0%`;
            if(message_time) {
                message_time *= 1000;
                if(this.progress_interval) {
                    clearInterval(this.progress_interval);
                }
                let progress = 100;
                this.progress_node.style = `transition: width ease 0s;--progress: ${progress}%`;

                this.progress_interval = setInterval(() => {
                    progress -= 1;
                    this.progress_node.style = `transition: width ease 1s;--progress: ${progress}%`;
                    if(progress <= 0) {
                        clearInterval(this.progress_interval);
                    }
                }, message_time / 100)
            }
        }else if(this.temp_message) {
            this.message = message;
        }
    }
}