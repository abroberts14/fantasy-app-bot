<!-- <template>
  <div class="card">
      <DataTable v-model:expandedRows="expandedRows" :value="products" dataKey="id"
              @rowExpand="onRowExpand" @rowCollapse="onRowCollapse" tableStyle="min-width: 60rem">
          <template #header>
              <div class="flex flex-wrap justify-content-end gap-2">
                  <Button text icon="pi pi-plus" label="Expand All" @click="expandAll" />
                  <Button text icon="pi pi-minus" label="Collapse All" @click="collapseAll" />
              </div>
          </template>
          <Column expander style="width: 5rem" />
          <Column field="name" header="Name"></Column>
          <Column header="Image">
              <template #body="slotProps">
                  <img :src="`https://primefaces.org/cdn/primevue/images/product/${slotProps.data.image}`" :alt="slotProps.data.image" class="shadow-4" width="64" />
              </template>
          </Column>
          <Column field="price" header="Price">
              <template #body="slotProps">
                  {{ formatCurrency(slotProps.data.price) }}
              </template>
          </Column>
          <Column field="category" header="Category"></Column>


          <template #expansion="slotProps">
              <div class="p-3">
                  <h5>Orders for {{ slotProps.data.name }}</h5>
                  <DataTable :value="slotProps.data.orders">
                      <Column field="id" header="Id" sortable></Column>
                      <Column field="customer" header="Customer" sortable></Column>
                      <Column field="date" header="Date" sortable></Column>
                      <Column field="amount" header="Amount" sortable>
                          <template #body="slotProps">
                              {{ formatCurrency(slotProps.data.amount) }}
                          </template>
                      </Column>

                      <Column headerStyle="width:4rem">
                          <template #body>
                              <Button icon="pi pi-search" />
                          </template>
                      </Column>
                  </DataTable>
              </div>
          </template>
      </DataTable>
  </div>
</template> -->
<template>
  <div class="card">
    <DataTable v-model:expandedRows="expandedRows" :value="products" dataKey="id"
      @rowExpand="onRowExpand" @rowCollapse="onRowCollapse" tableStyle="min-width: 60rem">
      <template #header>
        <div class="flex flex-wrap justify-content-end gap-2">
          <Button text icon="pi pi-plus" label="Expand All" @click="expandAll" />
          <Button text icon="pi pi-minus" label="Collapse All" @click="collapseAll" />
        </div>
      </template>
      <Column field="name" header="Name"></Column>
      <Column header="Image">
        <template #body="slotProps">
          <img :src="`https://primefaces.org/cdn/primevue/images/product/${slotProps.data.image}`" :alt="slotProps.data.image" class="shadow-4" width="64" />
        </template>
      </Column>
      <Column field="price" header="Price">
        <template #body="slotProps">
          {{ formatCurrency(slotProps.data.price) }}
        </template>
      </Column>
      <Column field="category" header="Category"></Column>
      <Column header="Expand Orders">
        <template #body="slotProps">
          <Button icon="pi pi-list" @click.stop="toggleOrders(slotProps.data)" />
        </template>
      </Column>
      <Column header="Expand Details">
        <template #body="slotProps">
          <Button icon="pi pi-info-circle" @click.stop="toggleDetails(slotProps.data)" />
        </template>
      </Column>

      <!-- Different expansions based on type -->
      <template #expansion="slotProps">
        <div v-if="expandedType[slotProps.data.id] === 'orders'" class="p-3">
          <h5>Orders for {{ slotProps.data.name }}</h5>
          <!-- Orders DataTable -->
          <DataTable :value="slotProps.data.orders">
            <Column field="id" header="Id" sortable></Column>
                      <Column field="customer" header="Customer" sortable></Column>
                      <Column field="date" header="Date" sortable></Column>
                      <Column field="amount" header="Amount" sortable>
                          <template #body="slotProps">
                              {{ formatCurrency(slotProps.data.amount) }}
                          </template>
                      </Column>

                      <Column headerStyle="width:4rem">
                          <template #body>
                              <Button icon="pi pi-search" />
                          </template>
                      </Column>
                  </DataTable>
          
        </div>
        <div v-else class="p-3">
          <h5>Details for {{ slotProps.data.name }}</h5>
          <!-- Details content here -->
        </div>
      </template>
    </DataTable>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import { useToast } from 'vue-toastification';

const products = ref();
const expandedRows = ref({});
const toast = useToast();
const expandedType = ref({}); // Stores type of expansion for each row
const getProductsData = () => {
            return [
                {
                    id: '1000',
                    code: 'f230fh0g3',
                    name: 'Bamboo Watch',
                    description: 'Product Description',
                    image: 'bamboo-watch.jpg',
                    price: 65,
                    category: 'Accessories',
                    quantity: 24,
                    inventoryStatus: 'INSTOCK',
                    rating: 5,
                    orders: [
                        {
                            id: '1027-0',
                            productCode: 'acvx872gc',
                            date: '2020-01-29',
                            amount: 89,
                            quantity: 1,
                            customer: 'Veronika Inouye',
                            status: 'DELIVERED'
                        },
                        {
                            id: '1027-1',
                            productCode: 'acvx872gc',
                            date: '2020-06-11',
                            amount: 89,
                            quantity: 1,
                            customer: 'Willard Kolmetz',
                            status: 'DELIVERED'
                        }
                    ]
                },
                {
                    id: '1001',
                    code: 'nvklal433',
                    name: 'Black Watch',
                    description: 'Product Description',
                    image: 'black-watch.jpg',
                    price: 72,
                    category: 'Accessories',
                    quantity: 61,
                    inventoryStatus: 'INSTOCK',
                    rating: 4,
                    orders: [
                        {
                            id: '1027-0',
                            productCode: 'acvx872gc',
                            date: '2020-01-29',
                            amount: 89,
                            quantity: 1,
                            customer: 'Veronika Inouye',
                            status: 'DELIVERED'
                        },
                        {
                            id: '1027-1',
                            productCode: 'acvx872gc',
                            date: '2020-06-11',
                            amount: 89,
                            quantity: 1,
                            customer: 'Willard Kolmetz',
                            status: 'DELIVERED'
                        }
                    ]
                },
                {
                    id: '1002',
                    code: 'zz21cz3c1',
                    name: 'Blue Band',
                    description: 'Product Description',
                    image: 'blue-band.jpg',
                    price: 79,
                    category: 'Fitness',
                    quantity: 2,
                    inventoryStatus: 'LOWSTOCK',
                    rating: 3
            },
        ];
};
onMounted(() => {
  products.value = getProductsData();
});
const toggleOrders = (product) => {
  if (expandedRows.value[product.id]) {
    expandedRows.value = {}; // Collapse all first
    expandedType.value[product.id] = undefined;
  } else {
    expandedRows.value = { [product.id]: true };
    expandedType.value[product.id] = 'orders'; // Set expansion type to 'orders'
  }
};
const toggleDetails = (product) => {
  if (expandedRows.value[product.id]) {
    expandedRows.value = {}; // Collapse all first
    expandedType.value[product.id] = undefined;
  } else {
    expandedRows.value = { [product.id]: true };
    expandedType.value[product.id] = 'details'; // Set expansion type to 'details'
  }
};
const onRowExpand = (event) => {
  toast.info('Product Expanded', event.data.name);
};
const onRowCollapse = (event) => {
  toast.info('Product Collapsed', event.data.name);
};
const expandAll = () => {
  expandedRows.value = products.value.reduce((acc, p) => (acc[p.id] = true) && acc, {});
};
const collapseAll = () => {
  expandedRows.value = null;
};
const formatCurrency = (value) => {
  return value.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
};
const getSeverity = (product) => {
  switch (product.inventoryStatus) {
      case 'INSTOCK':
          return 'success';

      case 'LOWSTOCK':
          return 'warning';

      case 'OUTOFSTOCK':
          return 'danger';

      default:
          return null;
  }
};
const getOrderSeverity = (order) => {
  switch (order.status) {
      case 'DELIVERED':
          return 'success';

      case 'CANCELLED':
          return 'danger';

      case 'PENDING':
          return 'warning';

      case 'RETURNED':
          return 'info';

      default:
          return null;
  }
};

</script>