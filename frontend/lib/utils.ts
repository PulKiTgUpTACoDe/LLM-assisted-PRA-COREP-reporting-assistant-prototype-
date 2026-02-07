export function cn(...inputs: (string | undefined | null | boolean)[]): string {
    return inputs.filter(Boolean).join(' ');
}

export function formatNumber(value: number, decimals: number = 0): string {
    return value.toLocaleString('en-GB', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
    });
}

export function formatCurrency(value: number, currency: string = 'GBP'): string {
    return new Intl.NumberFormat('en-GB', {
        style: 'currency',
        currency,
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(value);
}
