{% extends "base/base.html" %}
{% block start %}

<style>
  .filter-section {
    margin-bottom: 20px;
  }

  .form-group {
    margin-bottom: 10px;
  }

  @keyframes appear {
    from {
      opacity: 0;
      transform: scale(0.5);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }

  .card {
    animation: appear linear;
    animation-timeline: view();
    animation-range: entry 0% cover 40%;
  }

  .category-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .carousel-wrapper {
    position: relative;
    margin-bottom: 30px;
  }

  .category-carousel {
    display: flex;
    overflow-x: auto;
    scroll-behavior: smooth;
    gap: 1rem;
    padding-bottom: 10px;
    scroll-snap-type: x mandatory;
  }

  .category-carousel::-webkit-scrollbar {
    display: none;
  }

  .category-carousel .card {
    scroll-snap-align: start;
    flex: 0 0 auto;
    min-width: 180px;
    max-width: 220px;
  }

  .scroll-buttons {
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    transform: translateY(-50%);
    display: flex;
    justify-content: space-between;
    padding: 0 10px;
    z-index: 1;
  }

  .scroll-btn {
    background-color: #007bff;
    border: none;
    color: white;
    padding: 0.5rem 1rem;
    font-size: 1.2rem;
    border-radius: 5px;
    cursor: pointer;
    display: none;
  }

  @media (min-width: 768px) {
    .scroll-btn {
      display: inline-block;
    }
  }
</style>

<div class="container mt-3 pt-3">
  {% include 'base/alert.html' %}

  <!-- Category + Sort Header -->
  <div class="container my-4">
    <div class="category-header mb-3">
      <h3 class="mb-0">Shop by Category</h3>
      <form method="GET" class="form-inline">
        <div class="form-group">
          <label for="sort" class="mr-2">Sort by:</label>
          <select id="sort" name="sort" class="form-control" onchange="this.form.submit()">
            <option value="">Select</option>
            <option value="newest" {% if selected_sort == 'newest' %}selected{% endif %}>Newest</option>
            <option value="priceAsc" {% if selected_sort == 'priceAsc' %}selected{% endif %}>Price: Low-High</option>
            <option value="priceDesc" {% if selected_sort == 'priceDesc' %}selected{% endif %}>Price: High-Low</option>
          </select>
        </div>
      </form>
    </div>

    <!-- Category Carousel -->
    <div class="carousel-wrapper">
      <div class="scroll-buttons">
        <button class="scroll-btn" onclick="scrollCarousel(-1)">&#8592;</button>
        <button class="scroll-btn" onclick="scrollCarousel(1)">&#8594;</button>
      </div>

      <div class="category-carousel" id="categoryCarousel">
        {% for category in categories %}
        <div class="card">
          <img src="{{ category.category_image.url }}" class="card-img-top" alt="{{ category.category_name }}">
          <div class="card-body text-center">
            <h5 class="card-title">{{ category.category_name }}</h5>
            <a href="?category={{ category.category_name }}" class="btn btn-outline-primary">Browse</a>
          </div>
        </div>
        {% endfor %}
      </div>
    </div>
  </div>

  <!-- Products Section -->
  {% if selected_category %}
    <h4 class="mb-3">Products in "{{ selected_category }}"</h4>
  {% else %}
    <h4 class="mb-3">All Products</h4>
  {% endif %}

  <div class="row">
    {% for product in products %}
    <div class="col-md-3 col-6 mb-4">
      <figure class="card card-product-grid">
        <div class="img-wrap">
          <img src="/media/{{ product.product_images.first.image }}" class="w-100" />
        </div>
        <figcaption class="info-wrap border-top p-2">
          <a href="{% url 'get_product' product.slug %}" class="title d-block mb-1">
            <b>{{ product.product_name }}</b>
          </a>
          <div class="price text-success">₹{{ product.price }}.00</div>
        </figcaption>
      </figure>
    </div>
    {% endfor %}
  </div>

  <!-- Pagination -->
  <nav aria-label="Page navigation">
    <ul class="pagination justify-content-center mb-4">
      {% if products.has_previous %}
      <li class="page-item">
        <a class="page-link" href="?page={{ products.previous_page_number }}{% if selected_category %}&category={{ selected_category }}{% endif %}{% if selected_sort %}&sort={{ selected_sort }}{% endif %}">&laquo; Previous</a>
      </li>
      {% else %}
      <li class="page-item disabled"><a class="page-link">Previous</a></li>
      {% endif %}

      {% for num in products.paginator.page_range %}
      <li class="page-item {% if products.number == num %}active{% endif %}">
        <a class="page-link" href="?page={{ num }}{% if selected_category %}&category={{ selected_category }}{% endif %}{% if selected_sort %}&sort={{ selected_sort }}{% endif %}">{{ num }}</a>
      </li>
      {% endfor %}

      {% if products.has_next %}
      <li class="page-item">
        <a class="page-link" href="?page={{ products.next_page_number }}{% if selected_category %}&category={{ selected_category }}{% endif %}{% if selected_sort %}&sort={{ selected_sort }}{% endif %}">Next &raquo;</a>
      </li>
      {% else %}
      <li class="page-item disabled"><a class="page-link">Next</a></li>
      {% endif %}
    </ul>
  </nav>
</div>

<script>
  function scrollCarousel(direction) {
    const carousel = document.getElementById('categoryCarousel');
    const scrollAmount = 300;
    carousel.scrollBy({
      left: direction * scrollAmount,
      behavior: 'smooth'
    });
  }
</script>

{% endblock %}
