import { UseMutationOptions, UseQueryOptions } from "@tanstack/react-query";

export interface ServerPaginatedResult<T> {
  count: number;
  results: T[];
  next: null | string;
  previous: null | string;
}
export interface Category {
  id: number;
  image: string;
  name: string;
  description: string;
  is_active: boolean;
  parent: number;
}

export interface CartItem {
  id: number;
  product: {
    id: number;
    name: string;
    description: string;
    images: {
      id: number;
      image: string;
    }[];
  };
  quantity: number;
  store: Omit<Store, "address">;
  total_item_price: number;
  total_discount: number;
  total_price: number;
  unit_price: number;
  store_item: {
    discount_price: null | string;
    id: number;
    price: string;
    stock: number;
    store: number;
  };
}
export interface MyCart {
  items: CartItem[];
  total_price: number;
  total_discount: string;
}
export interface OrderItem {
  id: number;
  store_item: {
    id: number;
    product: Product;
    store: Omit<Store, "address">;
    price: string;
    discount_price: string;
    stock: number;
    is_active: boolean;
    created_at: string;
    updated_at: string;
  };
  quantity: number;
  price: string;
  total_price: string;
}
export enum OrderStatus {
  PENDING = 1,
  PROCESSING = 2,
  DELIVERED = 3,
  CANCELLED = 4,
  FAILED = 5,
}

export const OrderStatusDescriptionMap: Record<OrderStatus, string> = {
  [OrderStatus.PENDING]: "منتظر",
  [OrderStatus.PROCESSING]: "درحال پردازش",
  [OrderStatus.DELIVERED]: "تحویل شده",
  [OrderStatus.CANCELLED]: "لغو شده",
  [OrderStatus.FAILED]: "خطا",
};
export interface Order {
  id: number;
  customer: number;
  address: AddressType;
  status: OrderStatus;
  total_price: string;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
}
export interface Payment {
  id: number;
  status: number;
  transaction_id: string;
  amount: string;
  reference_id: string;
  card_pan: string;
  fee: string;
  created_at: string;
  updated_at: string;
  order: number;
}
export interface CreateProduct {
  name: string;
  description: string;
  is_active: boolean;
  categori: number;
  images: FileList;
}
export interface Product {
  id: number;
  name: string;
  rating: string;
  stock: string;
  best_seller: Seller | null;
  description: string;
  best_price: number | null;
  categories: Category[];
  images: {
    id: number;
    image: string;
  }[];
  is_active?: boolean;
}
export interface ProductDetails {
  id: number;
  best_seller: Seller | null;
  name: string;
  description: string;
  stock: number;
  rating: null | number;
  best_price: string;
  created_at: string;
  categories: Category[];
  images: {
    id: number;
    image: string;
  }[];
  sellers: Seller[];
  is_active?: boolean;
}
export interface Seller {
  id: number;
  name: string;
  product: number;
  price: string;
  discount_price: string;
  stock: number;
  detail_url: string;
  store: Omit<Store, "address">;
}
export interface Store {
  description: string;
  id: number;
  name: string;
  seller: string;
  address: AddressType[];
}
export interface Review {
  id: number;
  user: {
    first_name?: string;
    last_name?: string;
    username: string;
    user_url: string;
    picture: string;
  };
  rating: number;
  comment: string;
  created_at: string;
}
export interface PaginateQuery {
  page: number;
  page_size: number;
}

export type UserInfo = {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: null | string;
  is_seller: boolean;
  picture: string;
  address: AddressType[];
};
export type UserUpdateProfile = {
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
};
export type AddressCreateData = Omit<
  AddressType,
  "id" | "created_at" | "updated_at"
>;
export type AddressType = {
  id: number;
  label: string;
  address_line_1: string;
  address_line_2: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  created_at: string;
  updated_at: string;
};

export type RegisterStoreData = {
  name: string;
  description: string;
};

export type LoginRequestData = { username: string; password: string };
export type LoginResponseData = { refresh: string; access: string; user: UserInfo };

export type RegisterRequestData = {
  username: string;
};
export type RegisterResponseData = { message: string };

// Generic utility to infer mutation types from a mutation function
export type MutationOptionsFromFn<
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  TMutationFn extends (...args: any) => unknown,
  TContext = unknown,
> = Partial<
  UseMutationOptions<
    Awaited<ReturnType<TMutationFn>>, // success type
    Error, // error type
    Parameters<TMutationFn>[0], // variables/input type
    TContext // context type
  >
>;

// Generic utility to infer query options from a query function
export type QueryOptionsFromFn<
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  TQueryFn extends (...args: any) => unknown,
> = Partial<
  UseQueryOptions<
    Awaited<ReturnType<TQueryFn>>,
    Error,
    Awaited<ReturnType<TQueryFn>>
  >
>;
export interface CategoryQueryFilter extends PaginateQuery {
  is_active: boolean;
  name: string;
  parent: number;
}

export interface UserQueryFilter extends PaginateQuery {
  is_active: boolean;
  username: string;
  email: string;
}

export interface ProductsQueryFilter extends PaginateQuery {
  categories?: string[];
  name?: string;
  ordering?:
    | "created_at"
    | "-created_at"
    | "price"
    | "-price"
    | "rating"
    | "-rating";
  price_max?: number;
  price_min?: number;
}

export type StoreItemDetails = {
  id: number;
  price: string;
  discount_price: string;
  stock: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  product: Product;
};

export interface StoreItemQueryFilter extends PaginateQuery {
  is_active: boolean;
  name: string;
  stock_max: number;
  stock_min: number;
  created_at_after: string;
  created_at_before: string;
  ordering:
    | "created_at"
    | "-created_at"
    | "price"
    | "-price"
    | "discount_price"
    | "-discount_price"
    | "stock"
    | "-stock";
}
export type StoreItemCreate = {
  product: number;
  price: string;
  discount_price?: string;
  stock: number;
  is_active?: boolean;
};

export type ShopOrder = {
  id: number;
  status: OrderStatus;
  quantity: number;
  price: string;
  total_price: string;
  store_item: StoreItemDetails;
  user: UserInfo;
  address: string;
};
