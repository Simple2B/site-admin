import {Modal} from 'flowbite';
import type {ModalInterface} from 'flowbite';
import {modalOptions} from './utils';

export const stack = () => {
  const form = document.getElementById('add-stack-form') as HTMLFormElement;
  const inputElement = document.getElementById(
    'add-stack-form-input',
  ) as HTMLInputElement;
  const stacksDiv: HTMLElement = document.getElementById(
    'add-stack-form-stacks',
  );
  const scrfInput: HTMLInputElement = document.querySelector('#csrf_token');

  let oldSpansName: string[] = [];
  if (stacksDiv) {
    stacksDiv
      .querySelectorAll('span')
      .forEach(span => oldSpansName.push(span.textContent));
  }

  const $deleteStackModal: HTMLElement =
    document.querySelector('#deleteStackModal');

  let stackModalWarning: ModalInterface;

  if ($deleteStackModal) {
    stackModalWarning = new Modal($deleteStackModal, modalOptions);
  }

  // This selects elements where the id attribute starts with the string "button-"
  const listOfStacks = document.querySelectorAll('[id^="button-"]');

  if (listOfStacks) {
    listOfStacks.forEach(button => {
      const stackId = button.id.replace('button-', '');
      button.addEventListener('click', async () => {
        const response = await fetch(`/stack/delete/${stackId}`, {
          method: 'DELETE',
        });

        if (response.status == 200 || response.status == 422) {
          location.reload();
        }
      });
    });
  }

  if (form) {
    form.onkeydown = function (e) {
      if (e.key === 'Enter' && inputElement.value && stacksDiv) {
        e.preventDefault();

        const newStack = document.createElement('span');

        newStack.textContent = inputElement.value;
        newStack.setAttribute(
          'class',
          'bg-indigo-200 text-indigo-800 text-lg font-medium mr-2 px-2.5 py-0.5 rounded dark:bg-gray-700 dark:text-indigo-400 border border-indigo-400',
        );

        const newSpansName = Array.from(stacksDiv.querySelectorAll('span')).map(
          span => span.textContent,
        );

        if (
          !oldSpansName.includes(inputElement.value) &&
          !newSpansName.includes(inputElement.value)
        ) {
          stacksDiv.appendChild(newStack);
        }

        inputElement.value = '';
      }
    };
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();

    if (stacksDiv) {
      const newStacks = Array.from(stacksDiv.querySelectorAll('span'))
        .map(span => span.textContent)
        .filter(stack => !oldSpansName.includes(stack));

      if (
        inputElement &&
        inputElement.value &&
        !newStacks.includes(inputElement.value)
      ) {
        newStacks.push(inputElement.value);
      }

      const fetchStr = newStacks.join(',');

      if (fetchStr) {
        const formData = new FormData();
        formData.append('stacks', fetchStr);
        formData.append('csrf_token', scrfInput ? scrfInput.value : '');

        const response = await fetch(`/stack/create`, {
          method: 'POST',
          body: formData,
        });

        if (response.status == 200) {
          location.reload();
          inputElement.value = '';
        }
      }
    }
  }

  if (form) {
    form.addEventListener('submit', handleSubmit);
  }
};
