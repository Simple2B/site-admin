import {Modal} from 'flowbite';
import type {ModalOptions, ModalInterface} from 'flowbite';

export const stack = () => {
  const form = document.getElementById('add-stack-form') as HTMLFormElement;
  const name = document.getElementById(
    'add-stack-form-input',
  ) as HTMLInputElement;
  const stacksDiv = document.getElementById('add-stack-form-stacks');
  const scrfInput: HTMLInputElement = document.querySelector('#csrf_token');
  const oldSpansName = Array.from(stacksDiv.querySelectorAll('span')).map(
    span => span.textContent,
  );

  const listElementsCases = document.getElementById('listOfCases');
  const $deleteStackModal: HTMLElement =
    document.querySelector('#deleteStackModal');

  const modalOptions: ModalOptions = {
    backdrop: 'static',
    closable: true,
    onHide: () => {},
    onShow: () => {},
    onToggle: () => {},
  };

  const stackModalWarning: ModalInterface = new Modal(
    $deleteStackModal,
    modalOptions,
  );

  const stackModalCloseBtn = document.querySelector(
    '#modalStackCloseButtonError',
  );
  if (stackModalCloseBtn) {
    stackModalCloseBtn.addEventListener('click', () => {
      stackModalWarning.hide();
    });
  }

  document.querySelectorAll('[id^="button-"]').forEach(button => {
    const stackName = button.id.replace('button-', '');
    button.addEventListener('click', async () => {
      const formData = new FormData();
      formData.append('stacks', stackName);

      const response = await fetch(`/stack/delete`, {
        method: 'DELETE',
        body: formData,
      });

      if (response.status == 422) {
        const stringList = await response.json();

        // Clear existing content
        listElementsCases.innerHTML = '';

        // Create a <span> element for each string and append it to the container
        stringList.forEach((item: any) => {
          const span = document.createElement('span');
          const lineBreak = document.createElement('br');
          span.textContent = item;
          span.setAttribute('class', 'font-semibold text-xl');
          listElementsCases.appendChild(span);
          listElementsCases.appendChild(lineBreak);
        });

        stackModalWarning.show();
      }

      if (response.status == 200) {
        console.log('200');
        location.reload();
      }
    });
  });

  form.onkeydown = function (e) {
    if (e.keyCode == 13 && name.value && stacksDiv) {
      e.preventDefault();

      const newStack = document.createElement('span');

      newStack.textContent = name.value;
      newStack.setAttribute(
        'class',
        'bg-indigo-200 text-indigo-800 text-lg font-medium mr-2 px-2.5 py-0.5 rounded dark:bg-gray-700 dark:text-indigo-400 border border-indigo-400',
      );

      const newSpansName = Array.from(stacksDiv.querySelectorAll('span')).map(
        span => span.textContent,
      );

      if (
        !oldSpansName.includes(name.value) &&
        !newSpansName.includes(name.value)
      ) {
        stacksDiv.appendChild(newStack);
      }

      name.value = '';
    }
  };

  async function handleSubmit(event: Event) {
    event.preventDefault();

    const newStacks = Array.from(stacksDiv.querySelectorAll('span'))
      .map(span => span.textContent)
      .filter(stack => !oldSpansName.includes(stack));

    if (name && name.value && !newStacks.includes(name.value)) {
      newStacks.push(name.value);
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
        name.value = '';
      }
    }
  }

  form.addEventListener('submit', handleSubmit);
};
