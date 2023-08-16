import type { ModalOptions } from 'flowbite';
export declare const modalOptions: ModalOptions;
interface IConfirmModal {
    openModal: (textModal: string, confirmCallBack: () => void) => void;
}
declare const useConfirmModal: () => IConfirmModal;
export { useConfirmModal };
