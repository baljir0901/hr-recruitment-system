class RecruitmentForm {
    constructor() {
      this.form = document.getElementById('recruitmentForm');
      this.modal = document.getElementById('reviewModal');
      this.languageSelect = document.getElementById('languageSelect');
      this.confirmButton = document.getElementById('confirmSubmit');
      this.cancelButton = document.getElementById('cancelSubmit');
      this.imageInputs = document.querySelectorAll('input[type="file"]');
      
      this.setupEventListeners();
      this.setupImagePreviews();
    }
  
    setupEventListeners() {
      this.languageSelect.addEventListener('change', () => this.updateLanguage());
      this.form.addEventListener('submit', (e) => this.handleSubmit(e));
      this.confirmButton.addEventListener('click', () => this.submitForm());
      this.cancelButton.addEventListener('click', () => this.closeModal());
    }
  
    setupImagePreviews() {
      this.imageInputs.forEach(input => {
        input.addEventListener('change', (e) => this.handleImagePreview(e));
      });
    }
  
    handleImagePreview(event) {
      const file = event.target.files[0];
      const preview = event.target.parentElement.querySelector('.preview');
  
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);
      } else {
        preview.innerHTML = '';
      }
    }
  
    updateLanguage() {
      const lang = this.languageSelect.value;
      document.querySelectorAll(`[data-${lang}]`).forEach(element => {
        const translation = element.getAttribute(`data-${lang}`);
        if (lang === 'ja') {
          element.textContent = translation;
        } else {
          const japanese = element.getAttribute('data-ja');
          element.textContent = `${japanese} (${translation})`;
        }
      });
    }
  
    handleSubmit(e) {
      e.preventDefault();
      if (this.validateForm()) {
        this.showReviewModal();
      }
    }
  
    validateForm() {
      const requiredFields = this.form.querySelectorAll('[required]');
      let isValid = true;
  
      requiredFields.forEach(field => {
        if (!field.value.trim()) {
          isValid = false;
          this.showError(field);
        } else {
          this.clearError(field);
        }
      });
  
      return isValid;
    }
  
    showError(field) {
      const errorDiv = document.createElement('div');
      errorDiv.className = 'error-message';
      errorDiv.textContent = '必須項目です / This field is required';
      field.parentElement.appendChild(errorDiv);
    }
  
    clearError(field) {
      const errorDiv = field.parentElement.querySelector('.error-message');
      if (errorDiv) {
        errorDiv.remove();
      }
    }
  
    showReviewModal() {
      const formData = new FormData(this.form);
      let reviewContent = '<div class="review-items">';
      
      formData.forEach((value, key) => {
        if (key.startsWith('image')) {
          if (value.name) {
            reviewContent += `
              <div class="review-item">
                <strong>${key}:</strong> ${value.name}
              </div>
            `;
          }
        } else {
          reviewContent += `
            <div class="review-item">
              <strong>${key}:</strong> ${value}
            </div>
          `;
        }
      });
      
      reviewContent += '</div>';
      document.getElementById('reviewContent').innerHTML = reviewContent;
      this.modal.style.display = 'block';
    }
  
    closeModal() {
      this.modal.style.display = 'none';
    }
  
    async submitForm() {
      try {
        const formData = new FormData(this.form);
        const response = await fetch('/submit', {
          method: 'POST',
          body: formData
        });
  
        if (response.ok) {
          const result = await response.json();
          alert('提出が完了しました / Submission successful');
          this.form.reset();
          this.closeModal();
          // Clear image previews
          document.querySelectorAll('.preview').forEach(preview => {
            preview.innerHTML = '';
          });
        } else {
          throw new Error('提出に失敗しました / Submission failed');
        }
      } catch (error) {
        alert(error.message);
      }
    }
  }
  
  // Initialize the form when the DOM is loaded
  document.addEventListener('DOMContentLoaded', () => {
    new RecruitmentForm();
  });