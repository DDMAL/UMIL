import { PaginateBy } from './Types';

class PaginationManager {
  private pageNumInputs: NodeListOf<HTMLInputElement>;
  private pageBtns: NodeListOf<Element>;
  private optionRadios: NodeListOf<Element>;
  private instrumentNum: number;

  constructor() {
    const instrumentNumElement = document.getElementById('instrumentNum');
    this.instrumentNum = parseInt(
      instrumentNumElement.getAttribute('data-instrument-num'),
    );
    this.pageNumInputs = document.querySelectorAll(
      '.page-num',
    ) as NodeListOf<HTMLInputElement>;
    this.pageBtns = document.querySelectorAll('.page-link');
    this.optionRadios = document.querySelectorAll('.option-radio');

    this.initEventListeners();
    this.updatePaginationSetting();
  }

  private initEventListeners(): void {
    // Set up option radio buttons
    this.optionRadios.forEach((radio) => {
      if (radio.id === this.getPaginateBy().toString()) {
        (radio as HTMLInputElement).checked = true;
      }

      // Change event for radio buttons
      radio.addEventListener('change', () => {
        if ((radio as HTMLInputElement).checked) {
          const selectedOptionInt = parseInt(radio.id);
          this.setPaginateBy(selectedOptionInt as PaginateBy);
          const maxPageNum = Math.ceil(
            this.instrumentNum / this.getPaginateBy(),
          );
          const validPageNum = Math.min(
            Math.max(parseInt(this.getPage()), 1),
            maxPageNum,
          );

          if (validPageNum !== parseInt(this.getPage())) {
            this.setPage(validPageNum);
          }
          this.refreshPage();
        }
      });
    });

    // Enter key event for page number input
    this.pageNumInputs.forEach((input) => {
      input.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
          const maxPageNum = Math.ceil(
            this.instrumentNum / this.getPaginateBy(),
          );

          const validPageNum = Math.min(
            Math.max(parseInt(input.value), 1),
            maxPageNum,
          );

          input.value = validPageNum.toString();
          input.max = maxPageNum.toString();

          this.setPage(validPageNum);
          this.refreshPage();
        }
      });
    });

    // Click event for pagination buttons
    this.pageBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        (btn as HTMLAnchorElement).href = `${
          (btn as HTMLAnchorElement).href
        }&paginate_by=${this.getPaginateBy()}`;
      });
    });
  }

  private updatePaginationSetting(): void {
    const url = new URL(window.location.href);
    const page = url.searchParams.get('page') || '1';
    const paginateByStr = url.searchParams.get('paginate_by') || '20';

    this.setPage(page);
    this.setPaginateBy(this.parsePaginateBy(paginateByStr));
    this.pageNumInputs.forEach((input) => {
      input.max = Math.ceil(
        this.instrumentNum / parseInt(paginateByStr),
      ).toString();
    });
  }

  private parsePaginateBy(value: string | number): PaginateBy {
    const num = typeof value === 'string' ? parseInt(value) : value;
    return num === 20 || num === 50 || num === 100 ? (num as PaginateBy) : 20;
  }

  private setPaginateBy(paginateBy: PaginateBy): void {
    localStorage.setItem('paginate_by', paginateBy.toString());
  }

  private setPage(pageNum: string | number): void {
    localStorage.setItem('page', pageNum.toString());
  }

  private getPaginateBy(): PaginateBy {
    return parseInt(localStorage.getItem('paginate_by') || '20') as PaginateBy;
  }

  private getPage(): string {
    return localStorage.getItem('page') || '1';
  }

  private refreshPage(): void {
    const url = new URL(window.location.href);
    url.searchParams.set('page', this.getPage());
    url.searchParams.set('paginate_by', this.getPaginateBy().toString());
    window.location.href = url.href;
  }
}

// Initialize pagination when DOM is loaded
document.addEventListener('DOMContentLoaded', () => new PaginationManager());
